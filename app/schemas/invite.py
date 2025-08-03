from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class InviteBase(BaseModel):
    code: str
    is_active: bool
    expires_at: Optional[datetime] = None


class InviteCreate(BaseModel):
    expires_in_days: Optional[int] = Field(
        7,
        ge=1,
        le=365,
        description="Days until expiration (None for no expiration)",
    )


class InviteResponse(InviteBase):
    id: int
    created_by: int
    used_by: Optional[int] = None
    created_at: datetime
    used_at: Optional[datetime] = None
    creator_username: Optional[str] = None
    used_username: Optional[str] = None
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)


class InviteListResponse(BaseModel):
    invites: List[InviteResponse]
    total: int
    unused_count: int
    used_count: int
    expired_count: int
