from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["appdb"]
user_collection = db["users"]