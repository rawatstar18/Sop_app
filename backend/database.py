from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Initialize database connection"""
        try:
            self._client = MongoClient(settings.mongo_url)
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[settings.MONGO_DB_NAME]
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db_instance = Database()

def get_db():
    """Dependency to get database instance"""
    return db_instance.get_database()

# Collections
def get_user_collection():
    db = get_db()
    return db["users"]