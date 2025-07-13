from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class GuildBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


class GuildCreate(GuildBase):
    created_by: int = Field(..., description="User ID of the creator")


class GuildUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)


class GuildResponse(GuildBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
