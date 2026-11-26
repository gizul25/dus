from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import app.desk_reminder as desk_reminder
import app.routers.desk as desk_router
from app.desk_tracking import DeskPosition, DeskTracker, HeightReading, TimerProfile
from app.desk_tracking import TimerProfileRegistry


def test_tracker_snapshot_restores_active_timer_and_reminder_state():
    tracker = DeskTracker(TimerProfile(sitting_target_minutes=1))
    start = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    tracker.record(HeightReading(height_cm=65, recorded_at=start))
    status = tracker.record(
        HeightReading(height_cm=65, recorded_at=start + timedelta(minutes=1))
    )
    tracker.reminder_triggered = True

    restored = DeskTracker()
    restored.restore_snapshot(tracker.snapshot())

    assert status.reminder_due is True
    assert restored.position == DeskPosition.SITTING
    assert restored.position_seconds == 60
    assert restored.last_reading_at == start + timedelta(minutes=1)
    assert restored.current_period is not None
    assert restored.status().reminder_due is False


class MemoryCursor(list):
    def sort(self, key, direction=1):
        super().sort(key=lambda document: document.get(key), reverse=direction < 0)
        return self


class MemoryCollection:
    def __init__(self):
        self.documents = []

    def create_index(self, *args, **kwargs):
        return None

    def find_one(self, query):
        for document in self.documents:
            if self._matches(document, query):
                return dict(document)
        return None

    def find(self, query=None):
        return MemoryCursor(
            dict(document)
            for document in self.documents
            if self._matches(document, query or {})
        )

    def insert_one(self, document):
        saved = dict(document)
        saved.setdefault("_id", len(self.documents) + 1)
        self.documents.append(saved)

    def replace_one(self, query, replacement, upsert=False):
        for index, document in enumerate(self.documents):
            if self._matches(document, query):
                self.documents[index] = dict(replacement)
                return
        if upsert:
            self.documents.append(dict(replacement))

    def update_one(self, query, update, upsert=False):
        document = self.find_one(query)
        if document is None:
            if not upsert:
                return
            document = dict(query)
            self.documents.append(document)
        document.update(update.get("$set", {}))
        for index, saved in enumerate(self.documents):
            if self._matches(saved, query):
                self.documents[index] = document
                return

    def delete_one(self, query):
        self.documents = [
            document
            for document in self.documents
            if not self._matches(document, query)
        ]

    @staticmethod
    def _matches(document, query):
        for key, expected in query.items():
            if isinstance(expected, dict) and "$lte" in expected:
                if document.get(key, 0) > expected["$lte"]:
                    return False
            elif document.get(key) != expected:
                return False
        return True


class MemoryDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, MemoryCollection())

    def __getattr__(self, name):
        return self[name]


def test_tracker_and_reminder_state_survive_database_reload(monkeypatch):
    database = MemoryDatabase()
    profile = TimerProfile(sitting_target_minutes=1)
    monkeypatch.setattr(desk_router, "tracker", DeskTracker(profile))
    monkeypatch.setattr(
        desk_router,
        "profile_registry",
        TimerProfileRegistry(profile),
    )
    monkeypatch.setattr(desk_router, "tracker_sequence", 0)
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)
    database["reminder_preferences"].update_one(
        {"_id": "default"},
        {"$set": {"led_switch": True}},
        upsert=True,
    )
    request = SimpleNamespace(app=SimpleNamespace(db=database))
    start = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    desk_router.record_reading(
        HeightReading(height_cm=65, recorded_at=start),
        request,
    )
    due = desk_router.record_reading(
        HeightReading(height_cm=65, recorded_at=start + timedelta(minutes=1)),
        request,
    )

    assert due.reminder_due is True
    assert desk_reminder.ordinary_reminder_active is True

    desk_router.restore_desk_state(database)

    assert desk_router.tracker.position == DeskPosition.SITTING
    assert desk_router.tracker.position_seconds == 60
    assert desk_router.tracker.status().reminder_due is False
    assert len(desk_router.tracker.measurements.list()) == 2
    assert desk_reminder.ordinary_reminder_active is True
