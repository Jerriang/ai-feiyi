from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/guest", response_model=TokenResponse)
def guest_login():
    return TokenResponse(access_token=create_access_token("guest:anonymous"))


@router.post("/register", response_model=TokenResponse)
def register(payload: LoginRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="邮箱已存在")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(f"user:{user.id}"))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    return TokenResponse(access_token=create_access_token(f"user:{user.id}"))
