from pydantic import BaseModel, EmailStr, Field, field_validator 
from typing import Optional, Annotated, List
from bson import ObjectId
from datetime import datetime
from zoneinfo import ZoneInfo
import re

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    name: Optional[str]
    email: str
    role: str
    is_active: bool

class LoginUser(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SOPActivity(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    username: str
    sop_type: str = Field(..., description="Type of SOP (e.g., 'gift_sop')")
    task_id: str = Field(..., description="Unique identifier for the task")
    task_description: str = Field(..., description="Description of the completed task")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, datetime: str}
    }

class SOPActivityCreate(BaseModel):
    sop_type: str
    task_id: str
    task_description: str

class SOPActivityResponse(BaseModel):
    id: str
    user_id: str
    username: str
    sop_type: str
    task_id: str
    task_description: str
    completed_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

class SOPReport(BaseModel):
    user_id: str
    username: str
    sop_type: str
    total_tasks: int
    completed_tasks: int
    completion_percentage: float
    last_activity: Optional[datetime]
    activities: List[SOPActivityResponse]