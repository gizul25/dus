from app.desk_reminder import ReminderPreferences
from app.desk_reminder import reminder_functionality
import app.desk_reminder as desk_reminder
import asyncio

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
    desk_reminder.preferences = ReminderPreferences(
        forced_standup_switch = True
    )
    desk_reminder.forced_standup_active = False
    result = desk_reminder.is_forced_standup_reminder()
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

def test_ordinary_remineder_dismisial():
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
    desk_reminder.preferences = ReminderPreferences(
        led_switch = True
    )
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = False
    result = asyncio.run(desk_reminder.mock_timer())
    assert result == ["led_switch"] and desk_reminder.ordinary_reminder_active == True

def test_forced_standing_independent():
    desk_reminder.preferences = ReminderPreferences(
        forced_standup_switch = True
    )
    desk_reminder.forced_standup_active = False
    result = desk_reminder.is_forced_standup_reminder()
    assert result == True

def test_deactivation_when_standing_height_reached():
    desk_reminder.ordinary_reminder_active = True
    desk_reminder.forced_standup_active = True
    result = desk_reminder.check_height(100, 95)
    assert result == False and desk_reminder.ordinary_reminder_active == False
