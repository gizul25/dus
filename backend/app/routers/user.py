from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Literal
from ..dependencies import get_current_user
from ..desk_sessions import get_open_session_for_user

router = APIRouter(prefix="/user", tags=["user"])

SessionStatus = Literal["online", "away", "do not disturb", "offline"]

class UserProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    role: Literal["user", "admin"]
    mode: Literal["user", "admin"]
    session_id: str | None
    session_status: SessionStatus | None 

@router.get("/me", response_model=UserProfile)
def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    session = get_open_session_for_user(request.app.db, str(current_user["_id"]))
    
    return UserProfile(
        id=str(current_user["_id"]),
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        email=current_user["email"],
        role=current_user["role"],
        mode=request.state.login_mode,
        desk_id=current_user.get("desk_id"),
        session_id=session["_id"] if session else None,
        session_status=session["status"] if session else None,
    )
    
