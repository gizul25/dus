from unittest.mock import MagicMock
from app.desk_reminder import ReminderPreferences
from app.desk_reminder import reminder_functionality
import app.desk_reminder as desk_reminder
import pytest

def test_no_reminders_on():
    preferences = ReminderPreferences()
    result = reminder_functionality(preferences)
    assert result == []

def test_reminders_led_on():
    preferences = ReminderPreferences(
        led_switch = True
    )
    result = reminder_functionality(preferences)
    assert result == ["led_switch"]

def test_reminders_multiple_on():
    preferences = ReminderPreferences(
        notification_switch = True,
        buzzer_switch=True
    )
    result = reminder_functionality(preferences)
    assert result == ["notification_switch", "buzzer_switch"]

def test_forced_standup_only_on():
    preferences = ReminderPreferences(
        forced_standup_switch = True
    )
    desk_reminder.forced_standup_active = False
    result = desk_reminder.is_forced_standup_reminder(preferences)
    assert result == True

def test_below_min_standing_height():
    desk_reminder.forced_standup_active = True
    result = desk_reminder.check_height(90, 95)
    assert result == True

def test_above_min_standing_height():
    desk_reminder.forced_standup_active = True
    result = desk_reminder.check_height(100, 95)
    assert result == False

def test_at_min_standing_height():
    desk_reminder.forced_standup_active = True
    result = desk_reminder.check_height(95, 95)
    assert result == False

def test_ordinary_reminder_dismissial():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = desk_reminder.dismiss_reminder()
    assert result == False

def test_height_ordinary_reminder_stop():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = desk_reminder.check_height(100, 95)
    assert result == False and desk_reminder.ordinary_reminder_active == False

def test_ordinary_reminder_manual_dismissial():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = True
    result = desk_reminder.dismiss_reminder()
    assert result == True and desk_reminder.forced_standup_active == True

def  test_ordinary_reminder_below_min_standing_height():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = desk_reminder.check_height(90, 95)
    assert result == False and desk_reminder.ordinary_reminder_active == True

def test_multiple_dismissed_reminders():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = desk_reminder.dismiss_reminder()
    result1 = desk_reminder.dismiss_reminder()
    assert result == False and result1 == False

def test_repeated_time_activation():
    request = MagicMock()
    request.app.db.reminder_preferences.find_one.return_value = {
        "led_switch": True
    }
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = desk_reminder.mock_timer(request)
    assert result == ["led_switch"] and desk_reminder.ordinary_reminder_active == True

def test_forced_standing_independent():
    preferences = ReminderPreferences(
        forced_standup_switch = True
    )
    desk_reminder.forced_standup_active = False
    result = desk_reminder.is_forced_standup_reminder(preferences)
    assert result == True

def test_deactivation_when_standing_height_reached():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = True
    result = desk_reminder.check_height(100, 95)
    assert result == False and desk_reminder.ordinary_reminder_active == False

@pytest.mark.anyio
async def test_preferences_post(client):
    response = await client.post("/pref/" , json={
        "led_switch": True,
        "notification_switch": False,
        "buzzer_switch": True,
        "forced_standup_switch": False
    })

    response_get = await client.get("/pref/")

    assert response.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json() == response.json()

@pytest.mark.anyio
async def test_preferences_update(client):
    response = await client.post("/pref/" , json={
        "led_switch": True
    })

    response_another = await client.post("/pref/" , json={
        "led_switch": False,
        "buzzer_switch": True
    })

    response_get = await client.get("/pref/")

    assert response.status_code == 200
    assert response_another.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json() == response_another.json()

@pytest.mark.anyio
async def test_preferences_missing(client):
    response = await client.get("/pref/")

    assert response.status_code == 200
    assert response.json() == {
        "led_switch": False,
        "notification_switch": False,
        "buzzer_switch": False,
        "forced_standup_switch": False
    }

@pytest.mark.anyio
async def test_preferences_invalid(client):
    response = await client.post("/pref/", json={
        "led_switch": "invalid",
    })

    response_get = await client.get("/pref/")

    assert response.status_code == 422
    assert response_get.status_code == 200
    assert response_get.json() == {
        "led_switch": False,
        "notification_switch": False,
        "buzzer_switch": False,
        "forced_standup_switch": False
    }

@pytest.mark.anyio
async def test_preferences_partial(client):
    response = await client.post("/pref/" , json={
        "led_switch": True
    })

    response_get = await client.get("/pref/")
    assert response.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json() == {
        "led_switch": True,
        "notification_switch": False,
        "buzzer_switch": False,
        "forced_standup_switch": False
    }
