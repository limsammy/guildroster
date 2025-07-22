from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, List, Any
from datetime import datetime
from app.models.scenario import SCENARIO_DIFFICULTIES, SCENARIO_SIZES


class RaidBase(BaseModel):
    scheduled_at: datetime
    scenario_name: str = Field(
        ..., description="Scenario name this raid is for"
    )
    scenario_difficulty: str = Field(..., description="Scenario difficulty")
    scenario_size: str = Field(..., description="Scenario size")
    team_id: int = Field(..., description="Team ID this raid belongs to")
    warcraftlogs_url: Optional[str] = Field(
        None, description="Optional WarcraftLogs report URL for this raid"
    )

    @field_validator("warcraftlogs_url")
    @classmethod
    def validate_warcraftlogs_url(cls, v):
        if v is not None:
            # Basic validation - should contain warcraftlogs.com/reports/
            if "warcraftlogs.com/reports/" not in v:
                raise ValueError("Invalid WarcraftLogs URL format")
        return v

    @field_validator("scenario_difficulty")
    @classmethod
    def validate_scenario_difficulty(cls, v):
        if v not in SCENARIO_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("scenario_size")
    @classmethod
    def validate_scenario_size(cls, v):
        if v not in SCENARIO_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class RaidCreate(RaidBase):
    warcraftlogs_url: Optional[str] = Field(
        None, description="Optional WarcraftLogs report URL for this raid"
    )


class RaidUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    scenario_name: Optional[str] = Field(
        None, description="Scenario name this raid is for"
    )
    scenario_difficulty: Optional[str] = Field(
        None, description="Scenario difficulty"
    )
    scenario_size: Optional[str] = Field(None, description="Scenario size")
    team_id: Optional[int] = Field(
        None, description="Team ID this raid belongs to"
    )
    warcraftlogs_url: Optional[str] = Field(
        None, description="Optional WarcraftLogs report URL for this raid"
    )

    @field_validator("scenario_difficulty")
    @classmethod
    def validate_scenario_difficulty(cls, v):
        if v is not None and v not in SCENARIO_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("scenario_size")
    @classmethod
    def validate_scenario_size(cls, v):
        if v is not None and v not in SCENARIO_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class RaidResponse(RaidBase):
    id: int
    created_at: datetime
    updated_at: datetime
    warcraftlogs_report_code: Optional[str] = Field(
        None, description="WarcraftLogs report code extracted from URL"
    )
    warcraftlogs_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Stored WarcraftLogs report metadata"
    )
    warcraftlogs_participants: Optional[List[Dict[str, Any]]] = Field(
        None, description="Stored WarcraftLogs participant data"
    )
    warcraftlogs_fights: Optional[List[Dict[str, Any]]] = Field(
        None, description="Stored WarcraftLogs fight data"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
