import logging
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Body, Request, Response, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ...dependencies import get_token_header

logger = logging.getLogger(__name__)

# TODO: add token dependency once auth is implemented
router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

@router.get("/", response_model=List[User])
async def get_users(request: Request):
    col = request.app.db.users
    users = list(col.find(limit=100))
    return users

@router.get("/{id}", response_model=User)
def get_user(id: str, request: Request):
    col = request.app.db.users
    user = col.find_one({"_id": id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")
    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=str)
def create_user(request: Request, user: User = Body(...)):
    col = request.app.db.users
    user = jsonable_encoder(user)
    new_user = col.insert_one(user)

    return new_user.inserted_id

@router.put("/{id}", response_model=User)
def update_user(id: str, request: Request, user: UserUpdate = Body(...)):
    user = jsonable_encoder(user)
    col = request.app.db.users
    update_result = col.update_one(
        {"_id": id}, {"$set": user}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

    existing_user = col.find_one({"_id": id})
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")
    
    return existing_user

@router.delete("/{id}")
def delete_user(id: str, request: Request, response: Response):
    col = request.app.db.users
    delete_result = col.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")
    
    response.status_code = status.HTTP_204_NO_CONTENT
    return response