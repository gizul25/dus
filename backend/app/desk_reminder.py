from fastapi import APIRouter
from pydantic import BaseModel

class ReminderPreferences(BaseModel):
    led_switch: bool = False
    notification_switch : bool= False
    buzzer_switch: bool = False
    forced_standup_switch: bool = False

reminder = APIRouter()
preferences = ReminderPreferences()
forced_standup_active = False
ordinary_reminder_active = False

@reminder.post("/pref/")
async def pref(pref: ReminderPreferences):
    global preferences
    preferences = pref
    return pref

@reminder.get("/pref/")
async def pref():
    return preferences

def reminder_functionality(preferences: ReminderPreferences):
    reminder_dict = {
        "led_switch": preferences.led_switch,
        "notification_switch": preferences.notification_switch,
        "buzzer_switch": preferences.buzzer_switch,
    }

    reminder_list = []

    for(key, value) in reminder_dict.items():
        if value == True:
            reminder_list.append(key)
    return reminder_list

def is_forced_standup_reminder():
    global forced_standup_active
    forced_standup = preferences.forced_standup_switch
    if forced_standup:
        forced_standup_active = True
    return forced_standup_active

def check_height(height: int, min_height: int):
    global ordinary_reminder_active
    global forced_standup_active
    if forced_standup_active and height >= min_height:
        forced_standup_active = False
    if ordinary_reminder_active and height >= min_height:
        ordinary_reminder_active = False
    return forced_standup_active

def dismiss_reminder():
    global ordinary_reminder_active
    if forced_standup_active == False:
        ordinary_reminder_active = False
    return ordinary_reminder_active

@reminder.post("/mock_timer_timeout/")
async def mock_timer():
    global preferences
    global ordinary_reminder_active
    timer_end = reminder_functionality(preferences)
    if timer_end:
        ordinary_reminder_active = True
    return timer_end

@reminder.post("/mock_timer_timeout_optional_standup/")
async def mock_timer_optional_standup():
    global preferences
    timer_end = is_forced_standup_reminder()
    return timer_end

@reminder.post("/mock_height/")
async def mock_height(height: int):
    min_height = 95
    height = check_height(height, min_height)
    return height

@reminder.post("/dismissed_reminder/")
async def dismissed_reminder():
    result = dismiss_reminder()
    return result
