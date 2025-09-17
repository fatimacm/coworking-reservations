from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: RoleEnum = RoleEnum.user  # default user

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
