import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

from .desk_session_events import emit

logger = logging.getLogger(__name__)

SessionStatus = Literal["online", "away", "do not disturb", "offline"]
SessionFinishReason = Literal["timeout", "checkout"]

DEFAULT_TIMEOUT_NOTIFICATION_SECONDS = 30 * 60
DEFAULT_TIMEOUT_ACTION_SECONDS = 60 * 60


# ───────────────────────────────────────────────────────────── models


class DeskSession(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(alias="_id", serialization_alias="id")
    user_id: str
    desk_id: str
    status: SessionStatus
    started_at: datetime
    finished_at: datetime | None = None
    finished_reason: SessionFinishReason | None = None
    timeout_notification_at: datetime | None = None
    timeout_action_at: datetime | None = None
    timeout_notification_timer_id: str | None = None
    timeout_action_timer_id: str | None = None
    last_activity_at: datetime | None = None


class CheckInRequest(BaseModel):
    desk_id: str


class StatusUpdateRequest(BaseModel):
    status: SessionStatus


# ───────────────────────────────────────────────────────── exceptions


class SessionNotFound(Exception):
    def __init__(self, session_id: str) -> None:
        super().__init__(f"Desk session {session_id} not found")
        self.session_id = session_id


class SessionFinished(Exception):
    def __init__(self, session_id: str) -> None:
        super().__init__(f"Desk session {session_id} is already finished")
        self.session_id = session_id


class SessionConflict(Exception):
    """Raised when a user tries to open a second session, or loses a race."""


# ────────────────────────────────────────────────────────────── writes


async def start_session(
    db: Database,
    user_id: str,
    desk_id: str,
    *,
    timeout_notification_seconds: int = DEFAULT_TIMEOUT_NOTIFICATION_SECONDS,
    timeout_action_seconds: int = DEFAULT_TIMEOUT_ACTION_SECONDS,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    existing = db.desk_sessions.find_one({"user_id": user_id, "finished_at": None})
    if existing is not None:
        raise SessionConflict(f"User {user_id} already has open session {existing['_id']}")

    session = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "desk_id": desk_id,
        "status": "online",
        "started_at": now,
        "finished_at": None,
        "finished_reason": None,
        "timeout_notification_at": now + timedelta(seconds=timeout_notification_seconds),
        "timeout_action_at": now + timedelta(seconds=timeout_action_seconds),
        "timeout_notification_timer_id": None,
        "timeout_action_timer_id": None,
        "last_activity_at": now,
    }

    try:
        db.desk_sessions.insert_one(session)
    except DuplicateKeyError:
        raise SessionConflict(f"User {user_id} is already checked in")

    stored = db.desk_sessions.find_one({"_id": session["_id"]})
    emit(
        "desk_session_started",
        session_id=session["_id"],
        user_id=user_id,
        desk_id=desk_id,
    )
    return stored


def set_status(
    db: Database,
    session_id: str,
    new_status: SessionStatus,
) -> dict[str, Any]:
    session = db.desk_sessions.find_one({"_id": session_id})
    if session is None:
        raise SessionNotFound(session_id)
    if session["finished_at"] is not None:
        raise SessionFinished(session_id)

    old_status = session["status"]
    if old_status == new_status:
        return session

    now = datetime.now(timezone.utc)
    updated = db.desk_sessions.find_one_and_update(
        {"_id": session_id},
        {"$set": {"status": new_status, "last_activity_at": now}},
        return_document=ReturnDocument.AFTER,
    )
    emit(
        "status_changed",
        session_id=session_id,
        old_status=old_status,
        new_status=new_status,
    )
    return updated


def end_session(
    db: Database,
    session_id: str,
    reason: SessionFinishReason,
) -> dict[str, Any]:
    session = db.desk_sessions.find_one({"_id": session_id})
    if session is None:
        raise SessionNotFound(session_id)
    if session["finished_at"] is not None:
        return session  # already finished — return the stored doc

    now = datetime.now(timezone.utc)
    updated = db.desk_sessions.find_one_and_update(
        {"_id": session_id},
        {"$set": {
            "finished_at": now,
            "finished_reason": reason,
            "status": "offline",
            "last_activity_at": now,
            "timeout_notification_at": None,
            "timeout_action_at": None,
        }},
        return_document=ReturnDocument.AFTER,
    )

    _maybe_reset_desk_profile(db, session["desk_id"])

    emit(
        "desk_session_ended",
        session_id=session_id,
        reason=reason,
        user_id=session["user_id"],
        desk_id=session["desk_id"],
    )
    logger.info(
        "desk_session_ended id=%s user=%s desk=%s reason=%s",
        session_id, session["user_id"], session["desk_id"], reason,
    )
    return updated


# ─────────────────────────────────────────────────────────────── reads


def get_open_session_for_user(db: Database, user_id: str) -> dict | None:
    return db.desk_sessions.find_one({"user_id": user_id, "finished_at": None})


def get_open_sessions_for_desk(db: Database, desk_id: str) -> list[dict]:
    return list(db.desk_sessions.find({"desk_id": desk_id, "finished_at": None}))


# ──────────────────────────────────────────────────────── internal hooks


def _maybe_reset_desk_profile(db: Database, desk_id: str) -> None:
    others = db.desk_sessions.count_documents({"desk_id": desk_id, "finished_at": None})
    if others > 0:
        return
    logger.info(
        "desk_profile_reset_skipped desk=%s reason=feature_not_implemented",
        desk_id,
    )
    # TODO when profile storage exists:
    #   db.desk_profiles.delete_many({"desk_id": desk_id, "pending": True})
    #   default = category_default_for(desk_id)
    #   db.desk_profiles.update_one(
    #       {"desk_id": desk_id},
    #       {"$set": {"profile": default}},
    #       upsert=True,
    #   )