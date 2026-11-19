import os
import uuid

from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

mongo_client = MongoClient(os.environ["MONGODB_URL"])
db_name = os.environ["DBNAME"]
db = mongo_client[db_name]

doc = {"_id": "D-01", "name": "D-01"}
db["desks"].insert_one(doc)
doc = {"_id": "D-02", "name": "D-02"}
db["desks"].insert_one(doc)
doc = {"_id": "D-03", "name": "D-03"}
db["desks"].insert_one(doc)
doc = {"_id": "D-04", "name": "D-04"}
db["desks"].insert_one(doc)
doc = {"_id": "D-05", "name": "D-05"}
db["desks"].insert_one(doc)

now = datetime.now(timezone.utc)

doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "admin-user",
    "desk_id": "D-01",
    "position": "standing",
    "started_at": now - timedelta(minutes=30),
    "ended_at": now,
    "temperature_c": 32,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "admin-user",
    "desk_id": "D-01",
    "position": "sitting",
    "started_at": now - timedelta(minutes=323),
    "ended_at": now,
    "temperature_c": 20,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "test-user",
    "desk_id": "D-02",
    "position": "sitting",
    "started_at": now - timedelta(minutes=54),
    "ended_at": now,
    "temperature_c": 5,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "test-user",
    "desk_id": "D-04",
    "position": "standing",
    "started_at": now - timedelta(minutes=80),
    "ended_at": now,
    "temperature_c": 16,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "test-user",
    "desk_id": "D-03",
    "position": "sitting",
    "started_at": now - timedelta(minutes=3),
    "ended_at": now,
    "temperature_c": 17,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "test-user",
    "desk_id": "D-05",
    "position": "sitting",
    "started_at": now - timedelta(minutes=331),
    "ended_at": now,
    "temperature_c": 42,
}
db["periods"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "user_id": "admin-user",
    "desk_id": "D-01",
    "position": "standing",
    "started_at": now - timedelta(minutes=1),
    "ended_at": now,
    "temperature_c": 21,
}
db["periods"].insert_one(doc)

doc = {
    "_id": str(uuid.uuid4()),
    "message": "null pointer",
    "source": "manual",
    "severity": "warning",
    "context": "D-01",
    "received_at": datetime.now(timezone.utc),
}
db["frontend_errors"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "message": "test warning",
    "source": "manual",
    "severity": "warning",
    "context": "D-05",
    "received_at": datetime.now(timezone.utc),
}
db["frontend_errors"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "message": "test warning",
    "source": "manual",
    "severity": "warning",
    "context": "D-03",
    "received_at": datetime.now(timezone.utc),
}
db["frontend_errors"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "message": "test warning",
    "source": "manual",
    "severity": "warning",
    "context": "D-05",
    "received_at": datetime.now(timezone.utc),
}
db["frontend_errors"].insert_one(doc)
doc = {
    "_id": str(uuid.uuid4()),
    "message": "Black hole showed up and eaten half of the desk",
    "source": "manual",
    "severity": "error",
    "context": "D-05",
    "received_at": datetime.now(timezone.utc),
}
db["frontend_errors"].insert_one(doc)