from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import HeritageItem
from app.schemas import HeritageItemOut

router = APIRouter(prefix="/heritage-items", tags=["heritage"])


@router.get("", response_model=list[HeritageItemOut])
def list_items(city: str | None = None, db: Session = Depends(get_db)):
    query = db.query(HeritageItem).filter(HeritageItem.status == "published")
    if city:
        query = query.filter(HeritageItem.city == city)
    return query.order_by(HeritageItem.id.asc()).all()


@router.get("/{item_id}", response_model=HeritageItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(HeritageItem).filter(HeritageItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")
    return item
