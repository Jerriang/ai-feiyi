from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, verify_password
from app.db.database import get_db
from app.models import HeritageItem, User

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class HeritageUpdateRequest(BaseModel):
    description: str
    image_url: str


def get_current_admin(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or not str(payload.get("sub", "")).startswith("admin:"):
        raise HTTPException(status_code=403, detail="无管理员权限")
    user_id = int(str(payload["sub"]).split(":", 1)[1])
    user = db.query(User).filter(User.id == user_id, User.role == "admin").first()
    if not user:
        raise HTTPException(status_code=403, detail="无管理员权限")
    return user


@router.post("/login")
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.role == "admin").first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="管理员账号或密码错误")
    return {"access_token": create_access_token(f"admin:{user.id}"), "token_type": "bearer"}


@router.get("/me")
def me(current_admin: User = Depends(get_current_admin)):
    return {"id": current_admin.id, "email": current_admin.email, "nickname": current_admin.nickname}


@router.get("/heritage-items")
def list_heritage_items(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    items = db.query(HeritageItem).order_by(HeritageItem.id.asc()).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "city": i.city,
            "category": i.category,
            "summary": i.summary,
            "description": i.description,
            "image_url": i.image_url,
        }
        for i in items
    ]


@router.patch("/heritage-items/{item_id}")
def update_heritage_item(
    item_id: int,
    payload: HeritageUpdateRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.query(HeritageItem).filter(HeritageItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")
    item.description = payload.description.strip()
    item.image_url = payload.image_url.strip()
    db.commit()
    db.refresh(item)
    return {"id": item.id, "description": item.description, "image_url": item.image_url}


@router.get("/dashboard/overview")
def overview(_: User = Depends(get_current_admin)):
    return {
        "daily_visitors": 128,
        "guide_sessions": 86,
        "poster_generated": 49,
        "share_rate": 0.17,
    }
