from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient
import os

from .dependencies import get_query_token, get_token_header
from .routers.admin import users as admin_users
from .routers import items
from .ws import ws_app

backend_app = FastAPI(dependencies=[Depends(get_query_token)])

backend_app.include_router(items.router)
backend_app.include_router(admin_users.router)

@backend_app.get("/")
async def root():
    return {"message": "Hello from backend!"}