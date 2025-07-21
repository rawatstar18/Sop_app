from backend.models import User
from backend.database import user_collection
from passlib.hash import bcrypt

def addAdminIfNotFound():
    existing_admin = user_collection.find_one({"username": "sysadmin"})
    if not existing_admin:
        admin_user = User(
            name="System Admin",
            username="sysadmin",
            email="admin@admin.com",
            password=bcrypt.hash("systemadmin")
        )
        user_collection.insert_one(admin_user.dict())
        print("✅ Default admin user 'sysadmin' created")
