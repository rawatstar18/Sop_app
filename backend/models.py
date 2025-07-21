from pydantic import BaseModel

class User(BaseModel):
    username: str
    name: str
    email: str

class LoginUser(BaseModel):
    username: str
    password: str