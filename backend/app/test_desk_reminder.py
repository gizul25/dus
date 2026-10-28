from app.desk_reminder import ReminderPreferences
from app.desk_reminder import ReminderFunctionality

# Pytest - No reminders on
def test_no_reminders():
    preferences = ReminderPreferences()
    result = ReminderFunctionality(preferences)
    assert result == []

# Pytest - LED reminder on
def test_reminders_led():
    preferences = ReminderPreferences(
        led_switch = True
    )
    result = ReminderFunctionality(preferences)
    assert result == ["led_switch"]

# Pytest - Multiple reminders on
def test_reminders_multiple():
    preferences = ReminderPreferences(
        notification_switch = True,
        buzzer_switch=True
    )
    result = ReminderFunctionality(preferences)
    assert result == ["notification_switch", "buzzer_switch"]

# Pytest - Only optional forced standing on
def test_forced_standup():
    import app.desk_reminder as desk_reminder
    desk_reminder.preferences = ReminderPreferences(
        forced_standup_switch = True
    )
    desk_reminder.forced_standup_active = False
    result = desk_reminder.IsForcedStandupReminder()
    assert result == True

# Pytest - Height below standing min
def test_below_min_height():
    import app.desk_reminder as desk_reminder
    desk_reminder.forced_standup_active = True
    result = desk_reminder.Height(90, 95)
    assert result == True

# Pytest - Height above standing min
def test_above_min_height():
    import app.desk_reminder as desk_reminder
    desk_reminder.forced_standup_active = True
    result = desk_reminder.Height(100, 95)
    assert result == False