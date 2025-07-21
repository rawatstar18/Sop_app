from fastapi import APIRouter
from backend.models import User
from backend.database import users_collection

router = APIRouter()

@router.post("/users")
def create_user(user: User):
    result = users_collection.insert_one(user.dict())
    return {"message": "User created", "id": str(result.inserted_id)}
