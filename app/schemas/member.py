from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class MemberBase(BaseModel):
    display_name: str = Field(
        ..., min_length=1, max_length=50, description="Member's display name"
    )
    rank: str = Field("Member", max_length=20, description="Guild rank")
    guild_id: int = Field(..., description="Guild ID this member belongs to")


class MemberCreate(MemberBase):
    join_date: Optional[datetime] = Field(
        None, description="Member's join date"
    )


class MemberUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    rank: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class MemberResponse(MemberBase):
    id: int
    join_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
