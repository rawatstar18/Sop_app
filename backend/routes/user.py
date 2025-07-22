from fastapi import APIRouter, HTTPException, status, Depends, Form
from datetime import timedelta
from models import UserCreate, UserResponse, LoginUser, LoginResponse, Token
from database import get_user_collection
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_active_user
)
from config import settings
import logging

logger = logging.getLogger(__name__)
user_router = APIRouter()

@user_router.post("/register", response_model=dict)
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(None)
):
    """Register a new user"""
    try:
        user_collection = get_user_collection()
        
        # Check if user already exists
        if user_collection.find_one({"$or": [{"email": email}, {"username": username}]}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user
        user_data = {
            "username": username,
            "email": email,
            "name": name,
            "password": get_password_hash(password),
            "role": "user",
            "is_active": True
        }
        
        result = user_collection.insert_one(user_data)
        logger.info(f"User registered: {username}")
        
        return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@user_router.post("/login", response_model=LoginResponse)
async def login(user_data: LoginUser):
    """Authenticate user and return JWT token"""
    try:
        user_collection = get_user_collection()
        user = user_collection.find_one({"username": user_data.username})
        
        if not user or not verify_password(user_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        user_response = UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            name=user.get("name"),
            email=user["email"],
            role=user.get("role", "user"),
            is_active=user.get("is_active", True)
        )
        
        logger.info(f"User logged in: {user['username']}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@user_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        name=current_user.get("name"),
        email=current_user["email"],
        role=current_user.get("role", "user"),
        is_active=current_user.get("is_active", True)
    )

@user_router.put("/profile", response_model=dict)
async def update_profile(
    name: str = Form(None),
    email: str = Form(None),
    current_user: dict = Depends(get_current_active_user)
):
    """Update current user profile"""
    try:
        user_collection = get_user_collection()
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if email is not None:
            # Check if email is already taken by another user
            existing_user = user_collection.find_one({
                "email": email,
                "_id": {"$ne": current_user["_id"]}
            })
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            update_data["email"] = email
        
        if update_data:
            user_collection.update_one(
                {"_id": current_user["_id"]},
                {"$set": update_data}
            )
            logger.info(f"Profile updated: {current_user['username']}")
        
        return {"message": "Profile updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )