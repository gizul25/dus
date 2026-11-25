import os
import uuid
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

mongo_client = MongoClient(os.environ["MONGODB_URL"])
db = mongo_client[os.environ["DBNAME"]]

# ── Reference timestamps ────────────────────────────────────────────────
now = datetime.now(timezone.utc)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)


def _clamp_to_today(target: datetime) -> datetime:
    """If `target` lands before today's UTC midnight, anchor it just after
    midnight so the "today" timeframe still shows something."""
    if target < today_start:
        return today_start + (now - today_start) / 2
    return target


def today_hours_ago(hours: float) -> datetime:
    return _clamp_to_today(now - timedelta(hours=hours))


def today_minutes_ago(minutes: float) -> datetime:
    return _clamp_to_today(now - timedelta(minutes=minutes))


def days_ago(n: float) -> datetime:
    return now - timedelta(days=n)


# ── Verify prerequisite users exist ────────────────────────────────────
missing = [
    uid
    for uid in ("test-user", "admin-user")
    if db["users"].find_one({"_id": uid}) is None
]
if missing:
    raise SystemExit(f"Missing users: {missing}. Run seed_users.py first.")

# ── Cleanup (only seed-owned data) ─────────────────────────────────────
db["desk_sessions"].delete_many({"user_id": {"$in": ["test-user", "admin-user"]}})
db["periods"].delete_many({"user_id": {"$in": ["test-user", "admin-user"]}})
db["frontend_errors"].delete_many({"source": "manual"})
db["desks"].delete_many({"_id": {"$in": [f"D-0{i}" for i in range(1, 6)]}})


# ── Desks ──────────────────────────────────────────────────────────────
db["desks"].insert_many([{"_id": f"D-0{i}", "name": f"D-0{i}"} for i in range(1, 6)])


# ── Sessions + periods ─────────────────────────────────────────────────

sessions: list[dict] = []
periods: list[dict] = []


def add_session(
    user_id: str,
    desk_id: str,
    started_at: datetime,
    *,
    duration_min: float | None,
    position: str,
    temperature_c: float,
    humidity_pct: float,
    light: float,
    extra_periods: list[dict] | None = None,
) -> None:
    session_id = str(uuid.uuid4())

    if duration_min is None:
        finished_at = None
        status = "online"
        finished_reason = None
        period_end = max(now - timedelta(minutes=1), started_at + timedelta(seconds=30))
    else:
        finished_at = started_at + timedelta(minutes=duration_min)
        status = "offline"
        finished_reason = "checkout"
        period_end = finished_at

    sessions.append(
        {
            "_id": session_id,
            "user_id": user_id,
            "desk_id": desk_id,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "finished_reason": finished_reason,
            "timeout_notification_at": None,
            "timeout_action_at": None,
            "timeout_notification_timer_id": None,
            "timeout_action_timer_id": None,
            "last_activity_at": finished_at or now,
        }
    )

    periods.append(
        {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "desk_id": desk_id,
            "position": position,
            "started_at": started_at,
            "ended_at": period_end,
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct,
            "light": light,
            "height_cm": 110.0,
        }
    )

    for extra in extra_periods or []:
        periods.append(
            {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "desk_id": desk_id,
                "position": extra.get("position", "standing"),
                "started_at": extra["started_at"],
                "ended_at": extra.get("ended_at", period_end),
                "temperature_c": extra.get("temperature_c", temperature_c),
                "humidity_pct": extra.get("humidity_pct", humidity_pct),
                "light": extra.get("light", light),
                "height_cm": 110.0,
            }
        )


# ── Today: D-01 occupied by admin-user (4h so far) ─────────────────────
add_session(
    user_id="admin-user",
    desk_id="D-01",
    started_at=today_hours_ago(4),
    duration_min=None,
    position="sitting",
    temperature_c=22.5,
    humidity_pct=45.0,
    light=0.50,
    extra_periods=[
        {
            "position": "standing",
            "started_at": today_hours_ago(2.5),
            "ended_at": now - timedelta(minutes=1),
            "temperature_c": 22.7,
            "humidity_pct": 46.0,
            "light": 0.52,
        }
    ],
)

# ── Today: D-03 occupied by test-user (20m so far) ─────────────────────
add_session(
    user_id="test-user",
    desk_id="D-03",
    started_at=today_minutes_ago(20),
    duration_min=None,
    position="sitting",
    temperature_c=23.0,
    humidity_pct=42.0,
    light=0.70,
)

# ── Today: D-02 two short visits by test-user ──────────────────────────
add_session(
    user_id="test-user",
    desk_id="D-02",
    started_at=today_hours_ago(3),
    duration_min=45,
    position="sitting",
    temperature_c=21.8,
    humidity_pct=50.0,
    light=0.60,
)
add_session(
    user_id="test-user",
    desk_id="D-02",
    started_at=today_hours_ago(1.5),
    duration_min=30,
    position="standing",
    temperature_c=22.1,
    humidity_pct=48.0,
    light=0.55,
)

# ── Today: D-05 long session by test-user, split sit + stand ───────────
add_session(
    user_id="test-user",
    desk_id="D-05",
    started_at=today_hours_ago(5),
    duration_min=90,
    position="sitting",
    temperature_c=24.0,
    humidity_pct=55.0,
    light=0.40,
    extra_periods=[
        {
            "position": "standing",
            "started_at": today_hours_ago(3.75),
            "ended_at": today_hours_ago(3),
            "temperature_c": 24.1,
            "humidity_pct": 54.0,
            "light": 0.42,
        }
    ],
)

# ── Week: D-01 extra visit by test-user (3 days ago) ───────────────────
add_session(
    user_id="test-user",
    desk_id="D-01",
    started_at=days_ago(3),
    duration_min=120,
    position="sitting",
    temperature_c=21.5,
    humidity_pct=44.0,
    light=0.45,
)

# ── Week: D-04 two visits 5 days ago — two different users ─────────────
add_session(
    user_id="test-user",
    desk_id="D-04",
    started_at=days_ago(5),
    duration_min=180,
    position="sitting",
    temperature_c=20.5,
    humidity_pct=40.0,
    light=0.30,
)
add_session(
    user_id="admin-user",
    desk_id="D-04",
    started_at=days_ago(5.5),
    duration_min=120,
    position="standing",
    temperature_c=20.8,
    humidity_pct=42.0,
    light=0.35,
)

# ── Month: D-03 extra visit by admin-user (20 days ago) ────────────────
add_session(
    user_id="admin-user",
    desk_id="D-03",
    started_at=days_ago(20),
    duration_min=60,
    position="sitting",
    temperature_c=22.0,
    humidity_pct=46.0,
    light=0.50,
)

# ── Month: D-05 extra visit by admin-user (15 days ago) ────────────────
add_session(
    user_id="admin-user",
    desk_id="D-05",
    started_at=days_ago(15),
    duration_min=120,
    position="standing",
    temperature_c=23.5,
    humidity_pct=52.0,
    light=0.45,
)


db["desk_sessions"].insert_many(sessions)
db["periods"].insert_many(periods)


# ── Frontend errors / warnings ─────────────────────────────────────────

seed_errors = [
    {
        "desk_id": "D-01",
        "severity": "warning",
        "message": "Null pointer in state handler",
    },
    {"desk_id": "D-02", "severity": "error", "message": "Failed to sync desk state"},
    {
        "desk_id": "D-03",
        "severity": "warning",
        "message": "Height sensor reading out of range",
    },
    {"desk_id": "D-04", "severity": "error", "message": "Connection lost — retrying"},
    {
        "desk_id": "D-04",
        "severity": "error",
        "message": "Preset profile failed to load",
    },
    {"desk_id": "D-05", "severity": "warning", "message": "Test warning"},
    {"desk_id": "D-05", "severity": "warning", "message": "Test warning"},
    {
        "desk_id": "D-05",
        "severity": "error",
        "message": "Black hole showed up and ate half of the desk",
    },
]

db["frontend_errors"].insert_many(
    [
        {
            "_id": str(uuid.uuid4()),
            "message": e["message"],
            "source": "manual",
            "severity": e["severity"],
            "context": {"desk_id": e["desk_id"]},
            "received_at": now,
        }
        for e in seed_errors
    ]
)


# ── Summary ────────────────────────────────────────────────────────────

print("Seed complete.")
print()
print(f"  {db['desks'].count_documents({})} desks")
print(f"  {db['desk_sessions'].count_documents({})} desk sessions")
print(f"  {db['periods'].count_documents({})} periods")
print(
    f"  {db['frontend_errors'].count_documents({'source': 'manual'})} frontend errors"
)
print()
print("Expected state (used_min / unique_users):")
print("  Desk | Today      | Week       | Month")
print("  D-01 | 240m / 1u  | 360m / 2u  | 360m / 2u   (occupied)")
print("  D-02 |  75m / 1u  |  75m / 1u  |  75m / 1u")
print("  D-03 |  20m / 1u  |  20m / 1u  |  80m / 2u   (occupied)")
print("  D-04 |   0m / 0u  | 300m / 2u  | 300m / 2u")
print("  D-05 |  90m / 1u  |  90m / 1u  | 210m / 2u")
print()
print("Log in as test-user: user@example.com / test123")
