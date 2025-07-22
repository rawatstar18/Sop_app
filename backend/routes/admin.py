from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from models import UserCreate, UserUpdate, UserResponse
from database import get_user_collection
from auth import require_admin, get_password_hash
import logging

logger = logging.getLogger(__name__)
admin_router = APIRouter()

def user_serializer(user: dict) -> UserResponse:
    """Convert MongoDB document to UserResponse"""
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        name=user.get("name"),
        email=user["email"],
        role=user.get("role", "user"),
        is_active=user.get("is_active", True)
    )

@admin_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(require_admin)):
    """Get all users (admin only)"""
    try:
        user_collection = get_user_collection()
        users = list(user_collection.find({}))
        return [user_serializer(user) for user in users]
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@admin_router.post("/admin/users", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new user (admin only)"""
    try:
        user_collection = get_user_collection()
        
        # Check if user already exists
        if user_collection.find_one({"$or": [{"email": user_data.email}, {"username": user_data.username}]}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create user document
        new_user = {
            "username": user_data.username,
            "name": user_data.name,
            "email": user_data.email,
            "password": get_password_hash(user_data.password),
            "role": user_data.role,
            "is_active": True
        }
        
        result = user_collection.insert_one(new_user)
        logger.info(f"User created by admin: {user_data.username}")
        
        return {"message": "User created successfully", "user_id": str(result.inserted_id)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@admin_router.put("/admin/users/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update a user (admin only)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        user_collection = get_user_collection()
        
        # Build update data
        update_data = {}
        if user_data.username is not None:
            # Check if username is already taken
            existing_user = user_collection.find_one({
                "username": user_data.username,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            update_data["username"] = user_data.username
        
        if user_data.name is not None:
            update_data["name"] = user_data.name
        
        if user_data.email is not None:
            # Check if email is already taken
            existing_user = user_collection.find_one({
                "email": user_data.email,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            update_data["email"] = user_data.email
        
        if user_data.password is not None:
            update_data["password"] = get_password_hash(user_data.password)
        
        if user_data.role is not None:
            update_data["role"] = user_data.role
        
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated by admin: {user_id}")
        return {"message": "User updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@admin_router.delete("/admin/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a user (admin only)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        # Prevent admin from deleting themselves
        if str(current_user["_id"]) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        user_collection = get_user_collection()
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User deleted by admin: {user_id}")
        return {"message": "User deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@admin_router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Get a specific user by ID (admin only)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_serializer(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user by ID error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )