from contextlib import asynccontextmanager
import logging
import os
from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient
import pymongo

from .dependencies import get_query_token, get_token_header
from .routers.admin import users as admin_users, desks as admin_desks
from .routers import items
from .ws import ws_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('lifespan starting')

    app.mongo_client = pymongo.MongoClient(os.environ["MONGODB_URL"])
    db_name = os.environ["DBNAME"]
    app.db = app.mongo_client[db_name]

    logger.info('lifespan ready')

    yield

    logger.info('lifespan closing')

    app.mongo_client.close()
    app.mongo_client = None
    app.db = None

    logger.info('lifespan closed')

def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.include_router(items.router)
    app.include_router(admin_users.router)
    app.include_router(admin_desks.router)

    @app.get("/")
    async def root():
        return {"message": "Hello from backend!"}
    
    return app

backend_app = make_app(lifespan)