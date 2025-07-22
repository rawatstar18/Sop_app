from pymongo import MongoClient

client = client = client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
db = client["appdb"]
user_collection = db["users"]