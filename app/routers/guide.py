import time
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import ConversationHistory, HeritageItem
from app.services.guide import generate_story
from app.services.sse import chunk_text, sse_payload

router = APIRouter(prefix="/guide", tags=["guide"])


def _fake_vector(text: str) -> list[float]:
    nums = [ord(c) % 97 / 100 for c in text[:8]]
    return nums + [0.0] * (8 - len(nums))


def _compose_reply(item: HeritageItem, style: str, user_input: str, recent: list[ConversationHistory], concise: bool) -> str:
    history_summary = "；".join([h.summary_text for h in recent if h.summary_text])

    if user_input:
        if "再说一遍" in user_input:
            last_ai = next((h.summary_text for h in recent if h.role == "assistant" and h.summary_text), item.summary)
            return f"我再说一遍：{last_ai}"
        if "那个工艺是什么" in user_input or "工艺" in user_input:
            return f"你刚问到工艺，{item.name}的核心工艺是：{item.process}。"
        return f"结合你刚才的问题“{user_input}”，我补充说明：{item.meaning}。之前我们提到：{history_summary or item.summary}"

    sections = generate_story(item, style)
    text = "\n".join([sections["intro"], sections["body"], sections["qa"], sections["extension"], sections["summary"]])
    if concise:
        return f"简版导览：{item.name}重点在{item.process}，文化寓意是{item.meaning}。"
    return text


@router.get("/generate")
def generate(
    item_id: int = Query(..., ge=1),
    style: str = Query("历史叙事"),
    session_id: str = Query("default_session"),
    user_input: str = Query(""),
    user_id: int | None = Query(default=None),
    concise: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    item = db.query(HeritageItem).filter(HeritageItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")

    recent = (
        db.query(ConversationHistory)
        .filter(ConversationHistory.session_id == session_id, ConversationHistory.heritage_id == item_id)
        .order_by(ConversationHistory.created_at.desc())
        .limit(5)
        .all()
    )

    reply = _compose_reply(item, style, user_input, recent, concise)

    if user_input.strip():
        db.add(
            ConversationHistory(
                user_id=user_id,
                session_id=session_id,
                heritage_id=item_id,
                role="user",
                user_text=user_input.strip(),
                summary_text=user_input.strip()[:60],
                vector={"embedding": _fake_vector(user_input)},
            )
        )

    db.add(
        ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            heritage_id=item_id,
            role="assistant",
            user_text="",
            summary_text=reply[:120],
            vector={"embedding": _fake_vector(reply)},
        )
    )
    db.commit()

    def event_generator() -> Generator[str, None, None]:
        for piece in chunk_text(reply, 10):
            yield sse_payload(piece, False)
            time.sleep(0.08)
        yield sse_payload("", True)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
