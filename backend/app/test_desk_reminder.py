from desk_reminder import ReminderPreferences

reminder_preferences = ReminderPreferences()
print(reminder_preferences.led_switch)
print(reminder_preferences.buzzer_switch)
print(reminder_preferences.notification_switch)
print(reminder_preferences.forced_standup_switch)

reminder_preferences_true = ReminderPreferences(led_switch = True, buzzer_switch = False, notification_switch = True, forced_standup_switch = False)
print(reminder_preferences_true)

