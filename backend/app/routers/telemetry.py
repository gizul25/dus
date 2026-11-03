import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

FrontendErrorSource = Literal[
    "window.error",
    "unhandledrejection",
    "sveltekit",
    "manual",
]


class FrontendErrorIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    stack: str | None = Field(None, max_length=20_000)
    source: FrontendErrorSource = "manual"
    url: str | None = Field(None, max_length=2000)
    userAgent: str | None = Field(None, max_length=1000)
    occurredAt: datetime | None = None
    context: dict[str, Any] | None = None

    @field_validator("occurredAt")
    @classmethod
    def normalize_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class StoredFrontendError(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(alias="_id", serialization_alias="id")
    message: str
    stack: str | None = None
    source: FrontendErrorSource
    url: str | None = None
    user_agent: str | None = None
    occurred_at: datetime | None = None
    context: dict[str, Any] | None = None
    received_at: datetime
    client_host: str | None = None
    request_id: str | None = None


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client is not None else None


@router.post("/errors", status_code=status.HTTP_202_ACCEPTED)
def ingest_frontend_error(payload: FrontendErrorIn, request: Request) -> dict:
    received_at = datetime.now(timezone.utc)
    user_agent = payload.userAgent or request.headers.get("user-agent")

    document = {
        "_id": str(uuid.uuid4()),
        "message": payload.message,
        "stack": payload.stack,
        "source": payload.source,
        "url": payload.url,
        "user_agent": user_agent,
        "occurred_at": payload.occurredAt,
        "context": payload.context,
        "received_at": received_at,
        "client_host": _client_host(request),
        "request_id": request.headers.get("x-request-id"),
    }

    request.app.db.frontend_errors.insert_one(document)

    logger.warning(
        "frontend_error id=%s source=%s url=%s ua=%r message=%r",
        document["_id"],
        payload.source,
        payload.url,
        user_agent,
        payload.message,
    )
    if payload.stack:
        logger.warning("frontend_error stack:\n%s", payload.stack)
    if payload.context:
        logger.warning("frontend_error context=%r", payload.context)

    return {"status": "received", "id": document["_id"]}


@router.get("/errors", response_model=list[StoredFrontendError])
def list_frontend_errors(
    request: Request,
    limit: int = 100,
    source: FrontendErrorSource | None = None,
) -> list[StoredFrontendError]:
    limit = max(1, min(limit, 500))
    query: dict[str, Any] = {}
    if source is not None:
        query["source"] = source

    cursor = (
        request.app.db.frontend_errors.find(query)
        .sort("received_at", -1)
        .limit(limit)
    )
    return list(cursor)


@router.get("/errors/{error_id}", response_model=StoredFrontendError)
def read_frontend_error(error_id: str, request: Request) -> StoredFrontendError:
    document = request.app.db.frontend_errors.find_one({"_id": error_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Frontend error with ID {error_id} not found",
        )
    return document