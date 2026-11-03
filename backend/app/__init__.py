from contextlib import asynccontextmanager
import logging
import os

import pymongo
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import get_current_user
# from .internal import admin
from .routers import desk, items, users, auth
from .routers.admin import users as admin_users, desks as admin_desks

try:
    from .ws import ws_app
except ModuleNotFoundError:
    ws_app = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("lifespan starting")

    app.mongo_client = pymongo.MongoClient(os.environ["MONGODB_URL"])
    db_name = os.environ["DBNAME"]
    app.db = app.mongo_client[db_name]
    app.db["users"].create_index("email", unique=True)

    logger.info("lifespan ready")

    try:
        yield
    finally:
        logger.info("lifespan closing")
        app.mongo_client.close()
        app.mongo_client = None
        app.db = None
        logger.info("lifespan closed")


def make_app(lifespan):
    app = FastAPI(
        lifespan=lifespan,
    )

    app.include_router(users.router)
    app.include_router(items.router)
    app.include_router(desk.router)
    app.include_router(auth.router)

    app.include_router(admin_users.router)
    app.include_router(admin_desks.router)

    # app.include_router(
    #     admin.router,
    #     prefix="/admin",
    #     tags=["admin"],
    #     dependencies=[Depends(get_current_user)],
    #     responses={418: {"description": "I'm a teapot"}},
    # )

    @app.get("/")
    async def root():
        return {"message": "Hello from backend!"}

    return app


backend_app = make_app(lifespan)
backend_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)