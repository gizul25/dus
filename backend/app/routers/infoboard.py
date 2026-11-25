import logging
from datetime import datetime, timezone, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from ..dependencies import get_current_user
from ..desk_sessions import get_open_session_for_user, SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infoboard", tags=["infoboard"])

Timeframe = Literal["today", "week", "month", "all"]

class MeResponse(BaseModel):
    user_id: str
    name: str
    standing_min: int
    sitting_min: int
    desk_id: str | None
    status: SessionStatus | None = None
    session_started_at: datetime | None = None


class DeskResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    id: str = Field(alias="_id", serialization_alias="id")
    name: str
    occupied: bool
    time_used_min: float
    unique_users: int 
    temperature: float
    humidity: float 
    light: float
    errors: int
    warnings: int

def _timeframe_cutoff(timeframe: Timeframe) -> datetime | None:
    now = datetime.now(timezone.utc)
    if timeframe == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if timeframe == "week":
        return now - timedelta(days=7)
    if timeframe == "month":
        return now - timedelta(days=30)
    return None

def _to_aware_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _minutes(period: dict, now: datetime) -> float:
    started = _to_aware_utc(period["started_at"]) or now
    ended = _to_aware_utc(period.get("ended_at")) or now
    return max(0.0, (ended - started).total_seconds() / 60.0)


@router.get("/me", response_model=MeResponse)
def get_my_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> MeResponse:
    db = request.app.db
    user_id = str(current_user["_id"])
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    standing = sitting = 0.0
    for period in db.periods.find({"user_id": user_id, "started_at": {"$gte": today}}):
        m = _minutes(period, now)
        if period["position"] == "standing":
            standing += m
        else:
            sitting += m

    open_session = get_open_session_for_user(db, user_id)

    return MeResponse(
        user_id=user_id,
        name=f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        standing_min=round(standing),
        sitting_min=round(sitting),
        desk_id=open_session["desk_id"] if open_session else None,
        status=open_session["status"] if open_session else None,
        session_started_at=open_session["started_at"] if open_session else None,
    )


@router.get("/desks", response_model=list[DeskResponse])
def list_desk_stats(request: Request, timeframe: Timeframe = "today") -> list[DeskResponse]:
    db = request.app.db
    now = datetime.now(timezone.utc)
    cutoff = _timeframe_cutoff(timeframe)

    # ── sessions: time used + unique users (per desk, in timeframe) ─────
    session_match: dict = {}
    if cutoff is not None:
        session_match["started_at"] = {"$gte": cutoff}

    session_pipeline = [
        {"$match": session_match},
        {"$addFields": {
            "duration_min": {
                "$divide": [
                    {"$subtract": [{"$ifNull": ["$finished_at", now]}, "$started_at"]},
                    60000,
                ]
            }
        }},
        {"$group": {
            "_id": "$desk_id",
            "time_used_min": {"$sum": "$duration_min"},
            "unique_users_set": {"$addToSet": "$user_id"},
        }},
        {"$project": {
            "time_used_min": 1,
            "unique_users": {"$size": "$unique_users_set"},
        }},
    ]
    sessions_agg = {row["_id"]: row for row in db.desk_sessions.aggregate(session_pipeline)}

    # ── periods: environmental averages (per desk, in timeframe) ────────
    period_match: dict = {"ended_at": {"$ne": None}}
    if cutoff is not None:
        period_match["started_at"] = {"$gte": cutoff}

    period_pipeline = [
        {"$match": period_match},
        {"$group": {
            "_id": "$desk_id",
            "temperature": {"$avg": "$temperature_c"},
            "humidity": {"$avg": "$humidity_pct"},
            "light": {"$avg": "$light"},
        }},
    ]
    period_agg = {row["_id"]: row for row in db.periods.aggregate(period_pipeline)}

    # ── occupancy: right now (timeframe-independent) ────────────────────
    occupied_ids = {
        s["desk_id"]
        for s in db.desk_sessions.find({"finished_at": None}, {"desk_id": 1})
    }

    # ── errors / warnings: within timeframe ─────────────────────────────
    err_match: dict = {"severity": "error", "context.desk_id": {"$exists": True}}
    warn_match: dict = {"severity": "warning", "context.desk_id": {"$exists": True}}
    if cutoff is not None:
        err_match["received_at"] = {"$gte": cutoff}
        warn_match["received_at"] = {"$gte": cutoff}

    errors = {
        r["_id"]: r["count"]
        for r in db.frontend_errors.aggregate([
            {"$match": err_match},
            {"$group": {"_id": "$context.desk_id", "count": {"$sum": 1}}},
        ])
    }
    warnings = {
        r["_id"]: r["count"]
        for r in db.frontend_errors.aggregate([
            {"$match": warn_match},
            {"$group": {"_id": "$context.desk_id", "count": {"$sum": 1}}},
        ])
    }

    out: list[DeskResponse] = []
    for desk in db.desks.find():
        desk_id = str(desk["_id"])
        sess = sessions_agg.get(desk_id, {})
        per = period_agg.get(desk_id, {})
        out.append(DeskResponse(
            _id=desk_id,
            name=desk.get("name", desk_id),
            occupied=desk_id in occupied_ids,
            time_used_min=round(sess.get("time_used_min") or 0.0, 1),
            unique_users=int(sess.get("unique_users") or 0),
            temperature=round(per.get("temperature") or 0.0, 1),
            humidity=round(per.get("humidity") or 0.0, 1),
            light=round(per.get("light") or 0.0, 3),
            errors=errors.get(desk_id, 0),
            warnings=warnings.get(desk_id, 0),
        ))
    return out