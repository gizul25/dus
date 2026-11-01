from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Request

class ReminderPreferences(BaseModel):
    led_switch: bool = False
    notification_switch : bool= False
    buzzer_switch: bool = False
    forced_standup_switch: bool = False

reminder = APIRouter()
forced_standup_active = False
ordinary_reminder_active = False

@reminder.post("/pref/")
def pref(pref: ReminderPreferences, request: Request):
    col = request.app.db.reminder_preferences
    col.update_one( {"_id": "default"}, {"$set": pref.model_dump()}, upsert=True)
    return pref

@reminder.get("/pref/")
def pref(request: Request):
    return get_saved_preferences(request)


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

def is_forced_standup_reminder(preferences: ReminderPreferences):
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

def get_saved_preferences(request: Request):
    col = request.app.db.reminder_preferences
    saved_preferences = col.find_one({"_id": "default"})
    if saved_preferences is None:
        preferences = ReminderPreferences()
    else:
        preferences = ReminderPreferences.model_validate(saved_preferences)
    return preferences

@reminder.post("/mock_timer_timeout/")
def mock_timer(request: Request):
    global ordinary_reminder_active
    preferences = get_saved_preferences(request)
    timer_end = reminder_functionality(preferences)
    if timer_end:
        ordinary_reminder_active = True
    return timer_end

@reminder.post("/mock_timer_timeout_optional_standup/")
def mock_timer_optional_standup(request: Request):
    preferences = get_saved_preferences(request)
    timer_end = is_forced_standup_reminder(preferences)
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
