from backend.database import get_user_collection
from backend.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

async def create_default_admin():
    """Create default admin user if it doesn't exist"""
    try:
        user_collection = get_user_collection()
        
        # Check if admin already exists
        existing_admin = user_collection.find_one({"role": "admin"})
        if existing_admin:
            logger.info("Admin user already exists")
            return
        
        # Create default admin
        admin_user = {
            "username": "sysadmin",
            "name": "System Administrator",
            "email": "admin@example.com",
            "password": get_password_hash("admin123"),  # Change this in production!
            "role": "admin",
            "is_active": True
        }
        
        result = user_collection.insert_one(admin_user)
        logger.info(f"Default admin created with ID: {result.inserted_id}")
        logger.warning("Default admin password is 'admin123' - CHANGE THIS IN PRODUCTION!")
        
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")
        raise