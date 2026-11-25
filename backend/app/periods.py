import logging
import uuid
from datetime import datetime, timezone

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from .desk_tracking import HeightReading

logger = logging.getLogger(__name__)


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def record_transition(
    db: Database,
    user_id: str,
    reading: HeightReading,
    position: str,
) -> str | None:
    open_session = db.desk_sessions.find_one(
        {"user_id": user_id, "finished_at": None},
        {"_id": 1, "desk_id": 1},
    )
    if open_session is None:
        logger.info("period_skipped reason=no_open_session user=%s", user_id)
        return None

    effective_desk = open_session.get("desk_id")
    if effective_desk is None:
        logger.warning("period_skipped reason=session_missing_desk user=%s session=%s", user_id, open_session["_id"])
        return None

    now = _to_utc(reading.recorded_at) or datetime.now(timezone.utc)

    open_period = db.periods.find_one(
        {"user_id": user_id, "ended_at": None},
        sort=[("started_at", -1)],
    )

    desk_changed = open_period is not None and open_period["desk_id"] != effective_desk
    pos_changed = open_period is not None and open_period["position"] != position

    if open_period is not None and (desk_changed or pos_changed):
        db.periods.update_one(
            {"_id": open_period["_id"]},
            {"$set": {"ended_at": now}},
        )
        open_period = None

    if open_period is None:
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": open_session["_id"],
            "desk_id": effective_desk,
            "position": position,
            "started_at": now,
            "ended_at": None,
            "temperature_c": getattr(reading, "temperature_c", None),
            "humidity_pct": getattr(reading, "humidity_pct", None),
            "light": getattr(reading, "light", None),
            "height_cm": reading.height_cm,
        }
        try:
            db.periods.insert_one(doc)
        except DuplicateKeyError:
            existing = db.periods.find_one(
                {"user_id": user_id, "ended_at": None},
                sort=[("started_at", -1)],
            )
            return existing["desk_id"] if existing else None

    return effective_desk