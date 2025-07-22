from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    guild_id: int = Field(..., description="Guild ID this team belongs to")


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
