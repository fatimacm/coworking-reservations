from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: RoleEnum = RoleEnum.user  # default user

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class SpaceEnum(str, Enum):
    meeting_room_a = "meeting_room_a"
    meeting_room_b = "meeting_room_b"
    conference_hall = "conference_hall"
    desk_1 = "desk_1"
    desk_2 = "desk_2"
    desk_3 = "desk_3"

class StatusEnum(str, Enum):
    active = "active"
    cancelled = "cancelled"

class ReservationCreate(BaseModel):
    space_name: SpaceEnum
    start_datetime: datetime
    end_datetime: datetime

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    space_name: str
    start_datetime: datetime
    end_datetime: datetime
    status: StatusEnum
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReservationUpdate(BaseModel):
    space_name: Optional[SpaceEnum] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: Optional[StatusEnum] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    reservations: Optional[List[ReservationResponse]] = []

    class Config:
        from_attributes = True