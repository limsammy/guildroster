from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class RaidBase(BaseModel):
    scheduled_at: datetime
    scenario_id: int = Field(..., description="Scenario ID this raid is for")
    team_id: int = Field(..., description="Team ID this raid belongs to")


class RaidCreate(RaidBase):
    warcraftlogs_url: Optional[str] = Field(
        None, description="Optional WarcraftLogs report URL for this raid"
    )


class RaidUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    scenario_id: Optional[int] = Field(
        None, description="Scenario ID this raid is for"
    )
    team_id: Optional[int] = Field(
        None, description="Team ID this raid belongs to"
    )


class RaidResponse(RaidBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
