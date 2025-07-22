from fastapi import APIRouter, HTTPException, status, Depends, Form
from datetime import timedelta
from models import (
    UserCreate, UserResponse, LoginUser, LoginResponse, Token,
    SOPActivityCreate, SOPActivityResponse
)
from database import get_user_collection, get_sop_activity_collection
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_active_user
)
from config import settings
from fastapi import Request
from bson import ObjectId
from datetime import datetime
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
        logger.info(f"Login attempt for user: {user_data.username}")
        user_collection = get_user_collection()
        user = user_collection.find_one({"username": user_data.username})
        
        if not user or not verify_password(user_data.password, user["password"]):
            logger.warning(f"Failed login attempt for user: {user_data.username}")
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

@user_router.post("/sop/activity", response_model=dict)
async def log_sop_activity(
    activity_data: SOPActivityCreate,
    request: Request,
    current_user: dict = Depends(get_current_active_user)
):
    """Log SOP activity completion"""
    try:
        sop_collection = get_sop_activity_collection()
        
        # Check if this task was already completed by this user
        existing_activity = sop_collection.find_one({
            "user_id": current_user["_id"],
            "sop_type": activity_data.sop_type,
            "task_id": activity_data.task_id
        })
        
        if existing_activity:
            # Update existing activity with new timestamp
            sop_collection.update_one(
                {"_id": existing_activity["_id"]},
                {
                    "$set": {
                        "completed_at": datetime.utcnow(),
                        "ip_address": request.client.host,
                        "user_agent": request.headers.get("user-agent")
                    }
                }
            )
            logger.info(f"Updated SOP activity: {activity_data.task_id} for user: {current_user['username']}")
        else:
            # Create new activity record
            activity_record = {
                "user_id": current_user["_id"],
                "username": current_user["username"],
                "sop_type": activity_data.sop_type,
                "task_id": activity_data.task_id,
                "task_description": activity_data.task_description,
                "completed_at": datetime.utcnow(),
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "session_id": request.headers.get("x-session-id")
            }
            
            result = sop_collection.insert_one(activity_record)
            logger.info(f"Logged SOP activity: {activity_data.task_id} for user: {current_user['username']}")
        
        return {"message": "SOP activity logged successfully"}
    
    except Exception as e:
        logger.error(f"SOP activity logging error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log SOP activity"
        )

@user_router.get("/sop/activities", response_model=List[SOPActivityResponse])
async def get_user_sop_activities(
    sop_type: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user's SOP activities"""
    try:
        sop_collection = get_sop_activity_collection()
        
        query = {"user_id": current_user["_id"]}
        if sop_type:
            query["sop_type"] = sop_type
        
        activities = list(sop_collection.find(query).sort("completed_at", -1))
        
        return [
            SOPActivityResponse(
                id=str(activity["_id"]),
                user_id=str(activity["user_id"]),
                username=activity["username"],
                sop_type=activity["sop_type"],
                task_id=activity["task_id"],
                task_description=activity["task_description"],
                completed_at=activity["completed_at"],
                ip_address=activity.get("ip_address"),
                user_agent=activity.get("user_agent")
            )
            for activity in activities
        ]
    
    except Exception as e:
        logger.error(f"Get SOP activities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve SOP activities"
        )