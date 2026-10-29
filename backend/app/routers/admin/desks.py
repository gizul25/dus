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
    prefix="/admin/desks",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

class Desk(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)

class DeskUpdate(BaseModel):
    name: Optional[str]

@router.get("/", response_model=List[Desk])
async def get_desks(request: Request):
    col = request.app.db.desks
    desks = list(col.find(limit=100))
    return desks

@router.get("/{id}", response_model=Desk)
def get_desk(id: str, request: Request):
    col = request.app.db.desks
    desk = col.find_one({"_id": id})
    if desk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Desk with ID {id} not found")
    return desk

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=str)
def create_desk(request: Request, desk: Desk = Body(...)):
    col = request.app.db.desks
    desk = jsonable_encoder(desk)
    new_desk = col.insert_one(desk)

    return new_desk.inserted_id

@router.put("/{id}", response_model=Desk)
def update_desk(id: str, request: Request, desk: DeskUpdate = Body(...)):
    desk = jsonable_encoder(desk)
    col = request.app.db.desks
    update_result = col.update_one(
        {"_id": id}, {"$set": desk}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Desk with ID {id} not found")

    existing_desk = col.find_one({"_id": id})
    if existing_desk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Desk with ID {id} not found")
    
    return existing_desk

@router.delete("/{id}")
def delete_desk(id: str, request: Request, response: Response):
    col = request.app.db.desks
    delete_result = col.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Desk with ID {id} not found")
    
    response.status_code = status.HTTP_204_NO_CONTENT
    return response