# backend/routes/admin.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import List
from bson import ObjectId
from backend.database import user_collection
from backend.models import User

admin_router = APIRouter()

# Helper to convert MongoDB document to dict
def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    }

# Model for user creation
class CreateUserModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class UpdateUserModel(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

# GET all users
@admin_router.get("/admin/users", response_model=List[dict])
def get_users():
    users = user_collection.find()
    return [user_serializer(user) for user in users]

# POST create user
@admin_router.post("/admin/create")
def create_user(user: CreateUserModel):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = {
        "username": user.username,
        "email": user.email,
        "password": user.password
    }
    result = user_collection.insert_one(new_user)
    return {"message": "User created", "id": str(result.inserted_id)}

# PUT update user
@admin_router.put("/admin/update/{id}")
def update_user(id: str, user: UpdateUserModel):
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    result = user_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or unchanged")
    return {"message": "User updated"}

# DELETE user
@admin_router.delete("/admin/delete/{id}")
def delete_user(id: str):
    result = user_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
