from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Literal
from ..dependencies import JWT_SECRET, JWT_ALGORITHM, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False
    mode: Literal["user", "admin"] = "user"


def create_token(user_id: str, expiry_time: timedelta, mode: str = "user"):
    token_payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + expiry_time,
        "mode": mode,
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/login")
def login(credentials: LoginRequest, request: Request, response: Response):

    db = request.app.db

    user = db["users"].find_one({"email": credentials.email})

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    try:
        ph.verify(user["password"], credentials.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if credentials.mode == "admin" and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if credentials.remember_me:
        expiry_time = timedelta(days=30)
    else:
        expiry_time = timedelta(hours=1)  # for now

    token = create_token(str(user["_id"]), expiry_time, mode=credentials.mode)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=int(expiry_time.total_seconds()),
        path="/",
    )
    return {"message": "Login successful"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token", path="/", samesite="lax")
    return {"message": "Logout successful"}

