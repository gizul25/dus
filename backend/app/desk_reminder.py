from fastapi import FastAPI
from pydantic import BaseModel
import pymongo

class ReminderPreferences(BaseModel):
    led_switch: bool = False
    notification_switch : bool= False
    buzzer_switch: bool = False
    forced_standup_switch: bool = False

reminder = FastAPI()
preferences = ReminderPreferences()

@reminder.post("/pref/")
async def pref(pref: ReminderPreferences):
    global preferences
    preferences = pref
    return pref

@reminder.get("/pref/")
async def pref():
    return preferences


