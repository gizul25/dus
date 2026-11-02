from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError
from ..dependencies import JWT_SECRET, JWT_ALGORITHM, get_current_user
from ..database import db

router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


# For test purposes until users can registered
class User(BaseModel):
    fname: str
    lname: str
    email: str
    password: str
    role: str


def create_token(user_id: str, expiry_time: timedelta):
    token_payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + expiry_time}
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/login")
def login_user(credentials: LoginRequest, response: Response):

    user = db["users"].find_one({"email": credentials.email})

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    try:
        ph.verify(user["password"], credentials.password)

    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if credentials.remember_me:
        expiry_time = timedelta(days=30)
    else:
        expiry_time = timedelta(hours=1)   # for now

    token = create_token(str(user["_id"]), expiry_time)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=int(expiry_time.total_seconds()),
        path="/"
    )

    return {"message": "Login successful"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token", path="/", samesite="lax")
    return {"message": "Logout successful"}


# I will move this to admin once it will be merged
@router.post("/users")
def create_user_account(user: User):
    hashed_password = ph.hash(user.password)

    try:
        db["users"].insert_one(
            {
                "fname": user.fname,
                "lname": user.lname,
                "email": user.email,
                "password": hashed_password,
                "role": "user",
            }
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {
        "message": "User created successfully"
    }


# test
@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "fname": current_user["fname"],
        "lname": current_user["lname"],
        "role": current_user["role"],
    }
