from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import desk, items, users

try:
    from .ws import ws_app
except ModuleNotFoundError:
    ws_app = None

backend_app = FastAPI(dependencies=[Depends(get_query_token)])

backend_app.include_router(users.router)
backend_app.include_router(items.router)
backend_app.include_router(desk.router)
backend_app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@backend_app.get("/")
async def root():
    return {"message": "Hello from backend!"}
