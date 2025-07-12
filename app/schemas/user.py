from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    is_active: bool
    is_superuser: bool


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
