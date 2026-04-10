from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(80), default="游客")
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="visitor")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HeritageItem(Base):
    __tablename__ = "heritage_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(64))
    city: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    process: Mapped[str] = mapped_column(Text)
    meaning: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="published")

    contents: Mapped[list["HeritageContent"]] = relationship(back_populates="item")


class HeritageContent(Base):
    __tablename__ = "heritage_contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("heritage_items.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(32), default="knowledge")

    item: Mapped[HeritageItem] = relationship(back_populates="contents")


class RoutePlan(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("heritage_items.id"))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    travel_type: Mapped[str] = mapped_column(String(20))
    preference: Mapped[str] = mapped_column(String(32), default="balanced")
    reasoning: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    nodes: Mapped[list["RouteNode"]] = relationship(back_populates="route", cascade="all, delete")


class RouteNode(Base):
    __tablename__ = "route_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    node_order: Mapped[int] = mapped_column(Integer)
    node_title: Mapped[str] = mapped_column(String(120))
    stay_minutes: Mapped[int] = mapped_column(Integer)
    highlight: Mapped[str] = mapped_column(Text)
    skippable: Mapped[bool] = mapped_column(Boolean, default=False)

    route: Mapped[RoutePlan] = relationship(back_populates="nodes")


class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    route_id: Mapped[int | None] = mapped_column(ForeignKey("routes.id"))
    content_type: Mapped[str] = mapped_column(String(40), default="poster")
    template_id: Mapped[str] = mapped_column(String(80))
    preview_text: Mapped[str] = mapped_column(Text)
    share_slug: Mapped[str] = mapped_column(String(80), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True)
    heritage_id: Mapped[int] = mapped_column(ForeignKey("heritage_items.id"))
    role: Mapped[str] = mapped_column(String(20))
    user_text: Mapped[str] = mapped_column(Text, default="")
    summary_text: Mapped[str] = mapped_column(Text, default="")
    vector: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    exp: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(40), default="见习")
    badges: Mapped[dict] = mapped_column(JSON, default=list)
    completed_items: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamSession(Base):
    __tablename__ = "team_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    leader_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    member_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    heritage_id: Mapped[int] = mapped_column(ForeignKey("heritage_items.id"))
    latest_step: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
