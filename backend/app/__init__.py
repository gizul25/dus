from contextlib import asynccontextmanager
import logging
import os
from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient
import pymongo

from .dependencies import get_query_token, get_token_header
from .routers.admin import users as admin_users
from .routers import items
from .ws import ws_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

backend_app = FastAPI(dependencies=[Depends(get_query_token)])

@backend_app.on_event("startup")
def startup_db_client():
    logger.info('lifespan starting')
    backend_app.mongo_client = pymongo.MongoClient(os.environ["MONGODB_URL"])
    backend_app.db = backend_app.mongo_client.appdb
    logger.info('lifespan ready')

@backend_app.on_event("shutdown")
def shutdown_db_client():
    logger.info('lifespan closing')
    backend_app.mongo_client.close()
    backend_app.mongo_client = None
    backend_app.db = None
    logger.info('lifespan closed')


backend_app.include_router(items.router)
backend_app.include_router(admin_users.router)

@backend_app.get("/")
async def root():
    return {"message": "Hello from backend!"}