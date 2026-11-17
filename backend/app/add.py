import os
import uuid
from datetime import timedelta
import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient

mongo_client = MongoClient(os.environ["MONGODB_URL"])
db_name = os.environ["DBNAME"]
db = mongo_client[db_name]

password = "user123"
user = {
    "_id": str(uuid.uuid4()),
    "first_name": "Testing",
    "last_name": "User",
    "email": "user@example.com",
    "password": PasswordHasher().hash(password),
    "role": "user",
}
db["users"].insert_one(user)

password = "admin123"
user = {
    "_id": str(uuid.uuid4()),
    "first_name": "Testing",
    "last_name": "Admin",
    "email": "admin@example.com",
    "password": PasswordHasher().hash(password),
    "role": "admin",
}
db["users"].insert_one(user)