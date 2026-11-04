import os
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Cookie, Depends, HTTPException, Request

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"


def get_current_user(request: Request, access_token: str | None = Cookie(default=None)):

    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = request.app.db

    try:
        token_payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        request.state.login_mode = token_payload.get("mode")
        user_id = token_payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db["users"].find_one({"_id": user_id})

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_admin(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin" or request.state.login_mode != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user
