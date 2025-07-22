import os
from typing import Optional

class Settings:
    # Database Configuration
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", "27017"))
    MONGO_USERNAME: str = os.getenv("MONGO_USERNAME", "admin")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "admin")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "appdb")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:8080", "http://127.0.0.1:8080"]
    
    @property
    def mongo_url(self) -> str:
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource=admin"

settings = Settings()