from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import HeritageItem, User
from app.services.poster_image import render_poster_image

router = APIRouter(prefix="/generate", tags=["generate-image"])


class PosterImageRequest(BaseModel):
    user_id: int
    heritage_id: int
    template_style: str = "国风"


@router.post("/poster-image")
def poster_image(payload: PosterImageRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    heritage = db.query(HeritageItem).filter(HeritageItem.id == payload.heritage_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not heritage:
        raise HTTPException(status_code=404, detail="非遗项目不存在")

    filename = render_poster_image(
        heritage_name=heritage.name,
        user_nickname=user.nickname or "游客",
        heritage_image_url=heritage.image_url,
        template_style=payload.template_style,
        output_dir=Path("app/static/generated"),
    )
    return {"image_url": f"/static/generated/{filename}", "format": "png"}
