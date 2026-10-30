import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .internal import admin
from .routers import items, users, auth
from .ws import ws_app

backend_app = FastAPI()
backend_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

backend_app.include_router(users.router)
backend_app.include_router(items.router)
backend_app.include_router(auth.router)
backend_app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    ## dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@backend_app.get("/")
async def root():
    return {"message": "Hello from backend!"}