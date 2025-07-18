from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

from app.models.scenario import SCENARIO_DIFFICULTIES, SCENARIO_SIZES


class ScenarioBase(BaseModel):
    name: str = Field(..., max_length=100, description="Scenario name")
    difficulty: str = Field(
        ..., max_length=16, description="Scenario difficulty"
    )
    size: str = Field(..., max_length=4, description="Scenario size")
    is_active: bool = Field(True, description="Whether the scenario is active")

    @field_validator("name")
    @classmethod
    def validate_name_not_whitespace_only(cls, v):
        """Validate that name is not whitespace only."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        if v not in SCENARIO_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v not in SCENARIO_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=100, description="Scenario name"
    )
    difficulty: Optional[str] = Field(
        None, max_length=16, description="Scenario difficulty"
    )
    size: Optional[str] = Field(None, max_length=4, description="Scenario size")
    is_active: Optional[bool] = Field(
        None, description="Whether the scenario is active"
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_whitespace_only(cls, v):
        """Validate that name is not whitespace only."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty or whitespace only")
            return v.strip()
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        if v is not None and v not in SCENARIO_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {v}")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v is not None and v not in SCENARIO_SIZES:
            raise ValueError(f"Invalid size: {v}")
        return v


class ScenarioResponse(ScenarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
