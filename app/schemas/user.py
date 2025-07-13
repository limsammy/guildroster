from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    is_active: bool
    is_superuser: bool


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username for the account"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password for the account",
    )
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserLogin(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
