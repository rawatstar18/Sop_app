from backend.models import User
from backend.database import user_collection
from passlib.hash import bcrypt

def addAdminIfNotFound(user_collection):
    existing_admin = user_collection.find_one({"username": "sysadmin"})
    if not existing_admin:
        user_collection.insert_one({
            "username": "sysadmin",
            "password": "your_hashed_password",  # hash if needed
            "role": "admin"
        })
