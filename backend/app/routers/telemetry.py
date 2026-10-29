import logging
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class FrontendErrorIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    stack: str | None = Field(None, max_length=20_000)
    source: Literal[
        "window.error",
        "unhandledrejection",
        "sveltekit",
        "manual",
    ] = "manual"
    url: str | None = Field(None, max_length=2000)
    userAgent: str | None = Field(None, max_length=1000)
    occurredAt: datetime | None = None
    context: dict[str, Any] | None = None


@router.post("/errors", status_code=status.HTTP_202_ACCEPTED)
async def ingest_frontend_error(payload: FrontendErrorIn, request: Request) -> dict:
    logger.warning(
        "frontend_error source=%s url=%s ua=%r message=%r",
        payload.source,
        payload.url,
        payload.userAgent or request.headers.get("user-agent"),
        payload.message,
    )
    if payload.stack:
        logger.warning("frontend_error stack:\n%s", payload.stack)
    if payload.context:
        logger.warning("frontend_error context=%r", payload.context)

    return {"status": "received"}