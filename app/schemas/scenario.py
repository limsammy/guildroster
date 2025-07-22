from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.models.scenario import SCENARIO_DIFFICULTIES, SCENARIO_SIZES


class ScenarioBase(BaseModel):
    name: str = Field(..., max_length=100, description="Scenario name")
    is_active: bool = Field(True, description="Whether the scenario is active")
    mop: bool = Field(
        False,
        description="Whether this is a Mists of Pandaria scenario (affects available difficulties)",
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_whitespace_only(cls, v):
        """Validate that name is not whitespace only."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=100, description="Scenario name"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the scenario is active"
    )
    mop: Optional[bool] = Field(
        None,
        description="Whether this is a Mists of Pandaria scenario (affects available difficulties)",
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


class ScenarioResponse(ScenarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# New schemas for scenario variations
class ScenarioVariation(BaseModel):
    name: str = Field(..., description="Scenario name")
    difficulty: str = Field(..., description="Scenario difficulty")
    size: str = Field(..., description="Scenario size")
    display_name: str = Field(..., description="Display name for the variation")
    variation_id: str = Field(..., description="Unique variation identifier")

    # Note: difficulty and size are validated in the backend using the scenario template system.


class ScenarioWithVariations(ScenarioResponse):
    variations: List[ScenarioVariation] = Field(
        ..., description="All variations for this scenario"
    )


# Schema for raid scenario information
class RaidScenarioInfo(BaseModel):
    name: str = Field(..., description="Scenario name")
    difficulty: str = Field(..., description="Scenario difficulty")
    size: str = Field(..., description="Scenario size")
    display_name: str = Field(..., description="Display name for the variation")

    # Note: difficulty and size are validated in the backend using the scenario template system.
