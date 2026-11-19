import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infoboard", tags=["infoboard"])


class MeResponse(BaseModel):
    user_id: str
    name: str
    standing_min: int
    sitting_min: int
    desk_id: str | None


class DeskResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    id: str = Field(alias="_id", serialization_alias="id")
    name: str
    occupied: bool
    avg_sit_min: float
    avg_stand_min: float
    temperature: float
    errors: int
    warnings: int


def _to_aware_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _minutes(period: dict[str, Any], now: datetime) -> float:
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

    open_period = db.periods.find_one(
        {"user_id": user_id, "ended_at": None},
        sort=[("started_at", -1)],
    )

    return MeResponse(
        user_id=user_id,
        name=f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        standing_min=round(standing),
        sitting_min=round(sitting),
        desk_id=open_period["desk_id"] if open_period else None,
    )


@router.get("/desks", response_model=list[DeskResponse])
def list_desk_stats(request: Request) -> list[DeskResponse]:
    db = request.app.db

    pipeline = [
        {"$match": {"ended_at": {"$ne": None}}},
        {"$addFields": {
            "duration_min": {"$divide": [{"$subtract": ["$ended_at", "$started_at"]}, 60000]},
        }},
        {"$group": {
            "_id": "$desk_id",
            "avg_sit_min":   {"$avg": {"$cond": [{"$eq": ["$position", "sitting"]}, "$duration_min", None]}},
            "avg_stand_min": {"$avg": {"$cond": [{"$eq": ["$position", "standing"]}, "$duration_min", None]}},
            "temperature":   {"$avg": "$temperature_c"},
        }},
    ]
    agg = {row["_id"]: row for row in db.periods.aggregate(pipeline)}

    occupied_ids = {p["desk_id"] for p in db.periods.find({"ended_at": None}, {"desk_id": 1})}

    def _count(severity: str) -> dict[str, int]:
        return {
            r["_id"]: r["count"]
            for r in db.frontend_errors.aggregate([
                {"$match": {"severity": severity, "context.desk_id": {"$exists": True}}},
                {"$group": {"_id": "$context.desk_id", "count": {"$sum": 1}}},
            ])
        }
    errors = _count("error")
    warnings = _count("warning")

    out: list[DeskResponse] = []
    for desk in db.desks.find():
        desk_id = str(desk["_id"])
        row = agg.get(desk_id, {})
        out.append(DeskResponse(
            _id=desk_id,
            name=desk.get("name", desk_id),
            occupied=desk_id in occupied_ids,
            avg_sit_min=round(row.get("avg_sit_min") or 0.0, 1),
            avg_stand_min=round(row.get("avg_stand_min") or 0.0, 1),
            temperature=round(row.get("temperature") or 0.0, 1),
            errors=errors.get(desk_id, 0),
            warnings=warnings.get(desk_id, 0),
        ))
    return out