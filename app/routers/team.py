import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import TeamSession

router = APIRouter(prefix="/team", tags=["team"])


def _code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class TeamCreateReq(BaseModel):
    leader_user_id: int
    heritage_id: int


class TeamJoinReq(BaseModel):
    team_code: str
    member_user_id: int


class TeamProgressReq(BaseModel):
    team_code: str
    leader_user_id: int
    step: dict


@router.post("/create")
def create(payload: TeamCreateReq, db: Session = Depends(get_db)):
    code = _code()
    session = TeamSession(team_code=code, leader_user_id=payload.leader_user_id, heritage_id=payload.heritage_id)
    db.add(session)
    db.commit()
    return {"team_code": code}


@router.post("/join")
def join(payload: TeamJoinReq, db: Session = Depends(get_db)):
    session = db.query(TeamSession).filter(TeamSession.team_code == payload.team_code, TeamSession.status == "active").first()
    if not session:
        raise HTTPException(status_code=404, detail="组队码无效")
    session.member_user_id = payload.member_user_id
    db.commit()
    return {"ok": True, "heritage_id": session.heritage_id}


@router.post("/progress")
def progress(payload: TeamProgressReq, db: Session = Depends(get_db)):
    session = db.query(TeamSession).filter(TeamSession.team_code == payload.team_code, TeamSession.leader_user_id == payload.leader_user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="队伍不存在")
    session.latest_step = payload.step
    db.commit()
    return {"ok": True}


@router.get("/progress/{team_code}")
def poll(team_code: str, db: Session = Depends(get_db)):
    session = db.query(TeamSession).filter(TeamSession.team_code == team_code).first()
    if not session:
        raise HTTPException(status_code=404, detail="队伍不存在")
    return {"step": session.latest_step or {}, "member_user_id": session.member_user_id}


@router.post("/complete/{team_code}")
def complete(team_code: str, db: Session = Depends(get_db)):
    session = db.query(TeamSession).filter(TeamSession.team_code == team_code).first()
    if not session:
        raise HTTPException(status_code=404, detail="队伍不存在")
    session.status = "completed"
    db.commit()
    return {"ok": True, "leader_user_id": session.leader_user_id, "member_user_id": session.member_user_id}
