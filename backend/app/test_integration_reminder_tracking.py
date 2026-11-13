import pytest
import app.desk_reminder as desk_reminder
import app.routers.desk as desk_router
from app.desk_tracking import DeskTracker

@pytest.mark.anyio
async def test_reminder_when_timer_expires(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    result = await client.post(
        "/pref/",
        json={"led_switch": True}
    )
    assert result.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200
    assert readings.json()["reminder_due"] == False

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert readings_after.json()["reminder_due"] == True
    assert desk_reminder.ordinary_reminder_active == True

@pytest.mark.anyio
async def test_duplicate_reminder_prevention(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    result = await client.post(
        "/pref/",
        json={
            "led_switch": True
        }
    )

    assert result.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200
    assert readings.json()["reminder_due"] == False

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert readings_after.json()["reminder_due"] == True

    readings_after1 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:30+00:00"
        }
    )
    assert readings_after1.status_code == 200
    assert readings_after1.json()["reminder_due"] == False
    assert desk_reminder.ordinary_reminder_active == True

@pytest.mark.anyio
async def test_forced_standing_cannot_be_dismissed(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    result = await client.post(
        "/pref/",
        json={
            "forced_standup_switch": True
        }
    )
    assert result.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert desk_reminder.forced_standup_active == True

    dismiss = await client.post(
        "/dismissed_reminder/"
    )
    assert dismiss.status_code == 200
    assert desk_reminder.forced_standup_active == True

@pytest.mark.anyio
async def test_confirmed_standing_clear_reminder(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    result = await client.post(
        "/pref/",
        json={
            "forced_standup_switch": True
        }
    )
    assert result.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert desk_reminder.forced_standup_active == True

    clear = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:10+00:00"
        }
    )
    assert clear.status_code == 200
    assert clear.json()["position"] == "sitting"
    assert desk_reminder.forced_standup_active == True

    confirmed = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:16+00:00"
        }
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["position"] == "standing"
    assert desk_reminder.forced_standup_active == False

@pytest.mark.anyio
async def test_reminders_disabled(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    result = await client.post(
        "/pref/",
        json={
            "led_switch": False,
            "buzzer_switch": False,
            "notification_switch": False,
            "forced_standup_switch": False
        }
    )
    assert result.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert readings_after.json()["reminder_due"] == True
    assert desk_reminder.forced_standup_active == False
    assert desk_reminder.ordinary_reminder_active == False

@pytest.mark.anyio
async def test_invalid_height_reading(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": -10
        }
    )
    assert readings.status_code == 422

@pytest.mark.anyio
async def test_out_of_order_timestamps(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T11:59:00+00:00"
        }
    )
    assert readings_after.status_code == 422

    assert len(desk_router.tracker.measurements.list()) == 1

@pytest.mark.anyio
async def test_dismissal_blocked_during_forced_standing(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    reminders = await client.post(
        "/pref/",
        json={
            "led_switch": True,
            "forced_standup_switch": True
        }
    )
    assert reminders.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200

    dismiss = await client.post(
        "/dismissed_reminder/"
    )
    assert dismiss.status_code == 200
    assert desk_reminder.forced_standup_active == True
    assert desk_reminder.ordinary_reminder_active == True

@pytest.mark.anyio
async def test_reminder_at_exact_time(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200
    assert readings.json()["reminder_due"] == False

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:59+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert readings_after.json()["reminder_due"] == False

    readings_after1 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:00+00:00"
        }
    )
    assert readings_after1.status_code == 200
    assert readings_after1.json()["reminder_due"] == True

@pytest.mark.anyio
async def test_exact_standing_height_threshold(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    reminder = await client.post(
        "/pref/",
        json={"forced_standup_switch": True}
    )
    assert reminder.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert desk_reminder.forced_standup_active == True

    readings_after1 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 95,
            "recorded_at": "2026-11-03T12:01:10+00:00"
        }
    )
    assert readings_after1.status_code == 200
    assert desk_reminder.forced_standup_active == True
    assert readings_after1.json()["position"] == "sitting"

    readings_after2 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 95,
            "recorded_at": "2026-11-03T12:01:16+00:00"
        }
    )
    assert readings_after2.status_code == 200
    assert desk_reminder.forced_standup_active == False
    assert readings_after2.json()["position"] == "standing"

@pytest.mark.anyio
async def test_exact_position_confirm_time(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)
    reminder = await client.post(
        "/pref/",
        json={
            "forced_standup_switch": True
        }
    )
    assert reminder.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert desk_reminder.forced_standup_active == True

    readings_after1 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:10+00:00"
        }
    )
    assert readings_after1.status_code == 200
    assert desk_reminder.forced_standup_active == True

    readings_after2 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:14+00:00"
        }
    )
    assert readings_after2.status_code == 200
    assert desk_reminder.forced_standup_active == True

    readings_after3 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:15+00:00"
        }
    )
    assert readings_after3.status_code == 200
    assert desk_reminder.forced_standup_active == False

@pytest.mark.anyio
async def test_preferences_changed_during_reminder(client, monkeypatch):
    monkeypatch.setattr(desk_router, "tracker", DeskTracker())
    monkeypatch.setattr(desk_reminder, "ordinary_reminder_active", False)
    monkeypatch.setattr(desk_reminder, "forced_standup_active", False)

    reminder = await client.post(
        "/pref/",
        json={
            "led_switch": True,
            "forced_standup_switch": True
        }
    )
    assert reminder.status_code == 200

    response = await client.put(
        "/desk/profile",
        json={
            "seated_max_height_cm": 75,
            "standing_min_height_cm": 95,
            "sitting_target_minutes": 1,
            "standing_target_minutes": 10,
            "position_confirmation_seconds": 5
        }
    )
    assert response.status_code == 200

    readings = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:00:00+00:00"
        }
    )
    assert readings.status_code == 200

    readings_after = await client.post(
        "/desk/readings",
        json={
            "height_cm": 65,
            "recorded_at": "2026-11-03T12:01:01+00:00"
        }
    )
    assert readings_after.status_code == 200
    assert desk_reminder.forced_standup_active == True
    assert desk_reminder.ordinary_reminder_active == True

    response_after = await client.post(
        "/pref/",
        json={
            "led_switch": False,
            "forced_standup_switch": False
        }
    )
    assert response_after.status_code == 200
    assert desk_reminder.forced_standup_active == True
    assert desk_reminder.ordinary_reminder_active == True

    readings_after2 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:14+00:00"
        }
    )
    assert readings_after2.status_code == 200
    assert desk_reminder.forced_standup_active == True
    assert desk_reminder.ordinary_reminder_active == True

    readings_after3 = await client.post(
        "/desk/readings",
        json={
            "height_cm": 100,
            "recorded_at": "2026-11-03T12:01:19+00:00"
        }
    )
    assert readings_after3.status_code == 200
    assert desk_reminder.forced_standup_active == False
    assert desk_reminder.ordinary_reminder_active == False
    assert readings_after3.json()["position"] == "standing"


