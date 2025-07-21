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
