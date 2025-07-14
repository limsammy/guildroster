from pydantic import BaseModel, Field, validator
from typing import Optional
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
WOW_ROLES = ["DPS", "Healer", "Tank"]


class ToonBase(BaseModel):
    username: str = Field(..., max_length=50)
    class_: str = Field(..., alias="class", max_length=20)
    role: str = Field(..., max_length=20)
    is_main: bool = False

    @validator("class_")
    def validate_class(cls, v):
        if v not in WOW_CLASSES:
            raise ValueError(f"Invalid class: {v}")
        return v

    @validator("role")
    def validate_role(cls, v):
        if v not in WOW_ROLES:
            raise ValueError(f"Invalid role: {v}")
        return v


class ToonCreate(ToonBase):
    member_id: int


class ToonUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    class_: Optional[str] = Field(None, alias="class", max_length=20)
    role: Optional[str] = Field(None, max_length=20)
    is_main: Optional[bool] = None

    @validator("class_")
    def validate_class(cls, v):
        if v is not None and v not in WOW_CLASSES:
            raise ValueError(f"Invalid class: {v}")
        return v

    @validator("role")
    def validate_role(cls, v):
        if v is not None and v not in WOW_ROLES:
            raise ValueError(f"Invalid role: {v}")
        return v


class ToonResponse(ToonBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
