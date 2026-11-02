import os
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Cookie, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from .database import db


JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"


def get_current_user(access_token: str | None = Cookie(default=None)):

    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token_payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        user_id = token_payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db["users"].find_one({"_id": ObjectId(user_id)})

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except (InvalidTokenError, InvalidId):
        raise HTTPException(status_code=401, detail="Invalid token")
