from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class ScenarioBase(BaseModel):
    name: str = Field(..., max_length=100, description="Scenario name")
    is_active: bool = Field(True, description="Whether the scenario is active")

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
