import uuid
from datetime import datetime, timezone

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from .desk_tracking import HeightReading


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
    now = _to_utc(reading.recorded_at) or datetime.now(timezone.utc)

    user_doc = db.users.find_one({"_id": user_id}, {"desk_id": 1}) or {}
    effective_desk = reading.desk_id or user_doc.get("desk_id")

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

    if reading.desk_id and reading.desk_id != user_doc.get("desk_id"):
        db.users.update_one(
            {"_id": user_id},
            {"$set": {"desk_id": reading.desk_id}},
        )

    if open_period is None:
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "desk_id": effective_desk,
            "position": position,
            "started_at": now,
            "ended_at": None,
            "temperature_c": getattr(reading, "temperature_c", None),
            "height_cm": reading.height_cm,
        }
        try:
            db.periods.insert_one(doc)
        except DuplicateKeyError:
            pass

    return effective_desk