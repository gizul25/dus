import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pymongo import MongoClient

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
ph = PasswordHasher()
security = HTTPBearer()

JWT_SECRET = # configure 
JWT_ALGORITHM="HS256"

# For test purposes now
client = MongoClient("mongodb://root:password@database:27017?authSource=admin")
db = client["database"]


class LoginRequest(BaseModel):
    email: str
    password: str
    # remember_me: bool

# For test purposes until users can registered
class User(BaseModel):
    fname: str
    lname: str
    email: str
    password: str
    role: str

def create_token(user_id: str):
    token_payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hourse=1) # for now expires after 1h, change later
    }
    return jwt.encode(
        token_payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


@router.post("/login")
def login_user(credentials: LoginRequest):

    user = db["users"].find_one({"email: credentials.email"})

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    try:
        ph.verify(user["password"], credentials.password)
    
    except VerifyMismatchError:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_token(str(user["_id"]))

    return {
        "message": "Login successful",
        "token": token,
        "token_type": "bearer"
    }


@router.post("/logout")
