import os
from datetime import timedelta
import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient

mongo_client = MongoClient(os.environ["MONGODB_URL"])
db_name = os.environ["DBNAME"]
db = mongo_client[db_name]

password = "test123"
user = {
    "_id": "test-user",
    "first_name": "Testing",
    "last_name": "User",
    "email": "user@example.com",
    "password": PasswordHasher().hash(password),
    "role": "user",
}
db["users"].insert_one(user)

password = "admin123"
user = {
    "_id": "admin-user",
    "first_name": "Admino",
    "last_name": "Pro",
    "email": "admin@example.com",
    "password": PasswordHasher().hash(password),
    "role": "admin",
}
db["users"].insert_one(user)