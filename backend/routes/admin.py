from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from models import (
    UserCreate, UserUpdate, UserResponse,
    SOPActivityResponse, SOPReport
)
from database import get_user_collection, get_sop_activity_collection
from auth import require_admin, get_password_hash
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
import csv
import io
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
            detail="Failed to retrieve user")

@admin_router.get("/admin/sop/activities", response_model=List[SOPActivityResponse])
async def get_all_sop_activities(
    sop_type: str = None,
    user_id: str = None,
    days: int = 30,
    current_user: dict = Depends(require_admin)
):
    """Get all SOP activities (admin only)"""
    try:
        sop_collection = get_sop_activity_collection()
        
        # Build query
        query = {}
        if sop_type:
            query["sop_type"] = sop_type
        if user_id and ObjectId.is_valid(user_id):
            query["user_id"] = ObjectId(user_id)
        
        # Filter by date range
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query["completed_at"] = {"$gte": start_date}
        
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
        logger.error(f"Get all SOP activities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve SOP activities"
        )

@admin_router.get("/admin/sop/report")
async def download_sop_report(
    sop_type: str = None,
    user_id: str = None,
    days: int = 30,
    format: str = "csv",
    current_user: dict = Depends(require_admin)
):
    """Download SOP activity report (admin only)"""
    try:
        sop_collection = get_sop_activity_collection()
        user_collection = get_user_collection()
        
        # Build query
        query = {}
        if sop_type:
            query["sop_type"] = sop_type
        if user_id and ObjectId.is_valid(user_id):
            query["user_id"] = ObjectId(user_id)
        
        # Filter by date range
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query["completed_at"] = {"$gte": start_date}
        
        activities = list(sop_collection.find(query).sort("completed_at", -1))
        
        if format.lower() == "csv":
            # Create CSV report
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "User ID", "Username", "SOP Type", "Task ID", 
                "Task Description", "Completed At", "IP Address", "User Agent"
            ])
            
            # Write data
            for activity in activities:
                writer.writerow([
                    str(activity["user_id"]),
                    activity["username"],
                    activity["sop_type"],
                    activity["task_id"],
                    activity["task_description"],
                    activity["completed_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    activity.get("ip_address", ""),
                    activity.get("user_agent", "")
                ])
            
            output.seek(0)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"sop_report_{timestamp}.csv"
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format. Use 'csv'"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download SOP report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )

@admin_router.get("/admin/sop/summary", response_model=List[SOPReport])
async def get_sop_summary(
    sop_type: str = None,
    days: int = 30,
    current_user: dict = Depends(require_admin)
):
    """Get SOP completion summary by user (admin only)"""
    try:
        sop_collection = get_sop_activity_collection()
        user_collection = get_user_collection()
        
        # Get all users
        users = list(user_collection.find({}))
        
        # Build date filter
        date_filter = {}
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            date_filter = {"completed_at": {"$gte": start_date}}
        
        reports = []
        
        for user in users:
            query = {"user_id": user["_id"]}
            if sop_type:
                query["sop_type"] = sop_type
            query.update(date_filter)
            
            activities = list(sop_collection.find(query).sort("completed_at", -1))
            
            # Calculate statistics
            total_tasks = len(set(activity["task_id"] for activity in activities))
            last_activity = activities[0]["completed_at"] if activities else None
            
            # For now, assume 100% completion if any tasks are done
            # In a real scenario, you'd define the total expected tasks per SOP
            completion_percentage = 100.0 if total_tasks > 0 else 0.0
            
            activity_responses = [
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
            
            reports.append(SOPReport(
                user_id=str(user["_id"]),
                username=user["username"],
                sop_type=sop_type or "all",
                total_tasks=total_tasks,
                completed_tasks=total_tasks,
                completion_percentage=completion_percentage,
                last_activity=last_activity,
                activities=activity_responses
            ))
        
        return reports
    
    except Exception as e:
        logger.error(f"Get SOP summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate SOP summary"
        )