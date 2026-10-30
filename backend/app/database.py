from pymongo import MongoClient

# For test purposes now
client = MongoClient("mongodb://root:password@database:27017?authSource=admin")
db = client["database"]
db["users"].create_index("email", unique=True)