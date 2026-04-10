from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User, UserBehavior, UserProfile
from app.routers.admin import get_current_admin

router = APIRouter(prefix="/analytics", tags=["analytics"])

EXP_RULES = {
    "guide_complete": 50,
    "poster_generate": 20,
    "poster_share": 30,
}
LEVEL_RULES = [(1, "见习", 0), (2, "传承", 100), (3, "大师", 220)]


class TrackRequest(BaseModel):
    event_name: str
    properties: dict = Field(default_factory=dict)
    user_id: int | None = None
    session_id: str | None = None


def _ensure_profile(db: Session, user_id: int) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        return profile
    profile = UserProfile(user_id=user_id)
    db.add(profile)
    db.flush()
    return profile


def _apply_level(profile: UserProfile) -> tuple[bool, str | None]:
    old_level = profile.level
    new_level, new_title = 1, "见习"
    for level, title, need in LEVEL_RULES:
        if profile.exp >= need:
            new_level, new_title = level, title
    profile.level = new_level
    profile.title = new_title
    leveled = new_level > old_level
    return leveled, (f"恭喜晋升为【云锦守护人】" if leveled else None)


def _remaining_to_next(profile: UserProfile) -> int:
    targets = [need for _, _, need in LEVEL_RULES if need > profile.exp]
    return (min(targets) - profile.exp) if targets else 0


@router.post("/track")
def track(payload: TrackRequest, db: Session = Depends(get_db)):
    row = UserBehavior(
        user_id=payload.user_id,
        session_id=payload.session_id,
        behavior_type=payload.event_name,
        metadata=payload.properties,
    )
    db.add(row)

    result = {"ok": True}
    if payload.user_id:
        profile = _ensure_profile(db, payload.user_id)
        gained = EXP_RULES.get(payload.event_name, 0)
        profile.exp += gained

        if payload.event_name == "guide_complete":
            hid = payload.properties.get("heritage_id")
            completed = list(profile.completed_items or [])
            if hid and hid not in completed:
                completed.append(hid)
                profile.completed_items = completed

        if payload.event_name == "team_complete":
            badges = list(profile.badges or [])
            if "知音" not in badges:
                badges.append("知音")
                profile.badges = badges

        leveled, level_msg = _apply_level(profile)
        remaining = _remaining_to_next(profile)
        prompt = None
        if profile.title == "见习" and remaining <= 20:
            prompt = f"你还差 {remaining} 经验值晋升传承人，分享海报即可达成"

        hidden_story = None
        if len(list(profile.completed_items or [])) >= 3:
            hidden_story = "【非遗大师的私藏故事】你看到的纹样并非装饰，而是代代口传的密码。"

        result.update(
            {
                "exp_gained": gained,
                "profile": {
                    "level": profile.level,
                    "exp": profile.exp,
                    "title": profile.title,
                    "remaining_to_next": remaining,
                    "badges": profile.badges or [],
                },
                "level_up_message": level_msg,
                "next_goal_message": prompt,
                "hidden_story": hidden_story,
            }
        )

    db.commit()
    return result


@router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    guide_complete = (
        db.query(func.count(UserBehavior.id))
        .filter(UserBehavior.behavior_type == "guide_complete", UserBehavior.created_at >= start)
        .scalar()
        or 0
    )
    avg_duration = (
        db.query(func.avg(UserBehavior.metadata["duration_seconds"].as_integer()))
        .filter(UserBehavior.behavior_type == "guide_complete", UserBehavior.created_at >= start)
        .scalar()
        or 0
    )
    poster_generate = (
        db.query(func.count(UserBehavior.id))
        .filter(UserBehavior.behavior_type == "poster_generate", UserBehavior.created_at >= start)
        .scalar()
        or 0
    )
    poster_share = (
        db.query(func.count(UserBehavior.id))
        .filter(UserBehavior.behavior_type == "poster_share", UserBehavior.created_at >= start)
        .scalar()
        or 0
    )
    share_rate = round((poster_share / poster_generate), 4) if poster_generate else 0

    return {
        "guide_complete_today": int(guide_complete),
        "avg_guide_duration_seconds": float(avg_duration),
        "poster_generate_today": int(poster_generate),
        "poster_share_rate": share_rate,
        "bars": {"labels": ["导览完成", "海报生成", "海报分享"], "values": [guide_complete, poster_generate, poster_share]},
    }
