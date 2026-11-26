from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Literal
from ..dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

class UserProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    role: Literal["user", "admin"]
    mode: Literal["user", "admin"]

@router.get("/me", response_model=UserProfile)
def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    current_user["mode"] = request.state.login_mode
    current_user["id"] = str(current_user["_id"])
    return current_user


