from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

WOW_CLASSES = [
    "Death Knight",
    "Warrior",
    "Druid",
    "Paladin",
    "Monk",
    "Rogue",
    "Hunter",
    "Mage",
    "Warlock",
    "Priest",
    "Shaman",
]
WOW_ROLES = ["Melee DPS", "Ranged DPS", "Healer", "Tank"]


class ToonBase(BaseModel):
    username: str = Field(..., max_length=50)
    class_: str = Field(..., alias="class", max_length=20)
    role: str = Field(..., max_length=20)

    @field_validator("class_")
    @classmethod
    def validate_class(cls, v):
        if v not in WOW_CLASSES:
            raise ValueError(f"Invalid class: {v}")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in WOW_ROLES:
            raise ValueError(f"Invalid role: {v}")
        return v


class ToonUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    class_: Optional[str] = Field(None, alias="class", max_length=20)
    role: Optional[str] = Field(None, max_length=20)
    team_ids: Optional[List[int]] = None

    @field_validator("class_")
    @classmethod
    def validate_class(cls, v):
        if v is not None and v not in WOW_CLASSES:
            raise ValueError(f"Invalid class: {v}")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in WOW_ROLES:
            raise ValueError(f"Invalid role: {v}")
        return v


class ToonResponse(BaseModel):
    id: int
    username: str
    class_: str = Field(..., alias="class")
    role: str
    team_ids: List[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ToonCreate(ToonBase):
    team_ids: Optional[List[int]] = None
