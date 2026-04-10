from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import GeneratedContent
from app.schemas import PosterGenerateRequest
from app.services.poster import generate_poster_preview

router = APIRouter(prefix="/generated-contents", tags=["generate"])


@router.post("/posters")
def create_poster(payload: PosterGenerateRequest, db: Session = Depends(get_db)):
    preview, slug = generate_poster_preview(payload.template_id, payload.notes)
    record = GeneratedContent(
        route_id=payload.route_id,
        template_id=payload.template_id,
        preview_text=preview,
        share_slug=slug,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "preview_text": preview,
        "share_url": f"/share/{record.share_slug}",
    }
