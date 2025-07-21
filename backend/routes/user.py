from fastapi import APIRouter, HTTPException , Form
from backend.models import User, LoginUser
from backend.database import user_collection
from bson.objectid import ObjectId
from passlib.hash import bcrypt

user_router = APIRouter()

@user_router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    existing = user_collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hash(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password
    }

    user_collection.insert_one(user_data)
    return {"message": "User registered successfully"}


@user_router.post("/login")
def login(user: LoginUser):
    existing = user_collection.find_one({"username": user.username})
    if not existing or not bcrypt.verify(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful"}

# --- Admin: Get all users ---
@user_router.get("/admin/users")
def get_all_users():
    users = list(user_collection.find({}, {"password": 0}))  # Don't return passwords
    for user in users:
        user["_id"] = str(user["_id"])
    return users

# --- Admin: Create user ---
@user_router.post("/admin/create")
def create_user(user: User):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    user.password = bcrypt.hash(user.password)
    user_collection.insert_one(user.dict())
    return {"message": "User created successfully"}

# --- Admin: Delete user ---
@user_router.delete("/admin/delete/{user_id}")
def delete_user(user_id: str):
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# --- Admin: Update user ---
@user_router.put("/admin/update/{user_id}")
def update_user(user_id: str, user: User):
    updated_data = user.dict()
    updated_data["password"] = bcrypt.hash(user.password)  # Always re-hash
    result = user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}
