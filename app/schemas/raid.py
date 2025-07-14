from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

from app.models.raid import RAID_DIFFICULTIES, RAID_SIZES


class RaidBase(BaseModel):
    scheduled_at: datetime
    difficulty: str = Field(..., max_length=16)
    size: str = Field(..., max_length=4)
    team_id: int

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        if v not in RAID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v not in RAID_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class RaidCreate(RaidBase):
    pass


class RaidUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    difficulty: Optional[str] = Field(None, max_length=16)
    size: Optional[str] = Field(None, max_length=4)
    team_id: Optional[int] = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        if v is not None and v not in RAID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v is not None and v not in RAID_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class RaidResponse(RaidBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
