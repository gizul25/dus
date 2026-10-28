from fastapi import FastAPI
from pydantic import BaseModel


class ReminderPreferences(BaseModel):
    led_switch: bool = False
    notification_switch : bool= False
    buzzer_switch: bool = False
    forced_standup_switch: bool = False

reminder = FastAPI()
preferences = ReminderPreferences()
forced_standup_active = False

@reminder.post("/pref/")
async def pref(pref: ReminderPreferences):
    global preferences
    preferences = pref
    return pref

@reminder.get("/pref/")
async def pref():
    return preferences

def ReminderFunctionality(ReminderPreferences: ReminderPreferences):
    reminder_dict = {
        "led_switch": ReminderPreferences.led_switch,
        "notification_switch": ReminderPreferences.notification_switch,
        "buzzer_switch": ReminderPreferences.buzzer_switch,
    }

    reminder_list = []

    for(key, value) in reminder_dict.items():
        if value == True:
            reminder_list.append(key)
    return reminder_list

def IsForcedStandupReminder():
    global forced_standup_active
    forced_standup = preferences.forced_standup_switch
    if forced_standup:
        forced_standup_active = True
    return forced_standup_active

def Height(height: int, min_height: int):
    global forced_standup_active
    if forced_standup_active and height >= min_height:
        forced_standup_active = False
    return forced_standup_active


@reminder.post("/mock_timer_timeout/")
async def mock_timer():
    global preferences
    timer_end = ReminderFunctionality(preferences)
    return timer_end

@reminder.post("/mock_timer_timeout_optional_standup/")
async def mock_timer_optional_standup():
    global preferences
    timer_end = IsForcedStandupReminder()
    return timer_end

@reminder.post("/mock_height/")
async def mock_height(height: int):
    min_height = 95
    height = Height(height, min_height)
    return height