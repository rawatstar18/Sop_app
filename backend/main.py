from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from backend.routes.user import user_router
import hashlib

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["mydatabase"]
users_collection = db["users"]


# Models
class LoginRequest(BaseModel):
    email: str
    password: str

# Password hashing helper
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Login route
@app.post("/login")
async def login(data: LoginRequest):
    user = users_collection.find_one({"email": data.email})
    if not user or user["password"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "email": user["email"]}
