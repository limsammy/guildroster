from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class AttendanceBase(BaseModel):
    raid_id: int = Field(
        ..., description="Raid ID this attendance record is for"
    )
    toon_id: int = Field(
        ..., description="Toon ID this attendance record is for"
    )
    is_present: bool = Field(
        True, description="Whether the toon was present at the raid"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about attendance"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or whitespace only")
        return v


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    is_present: Optional[bool] = Field(
        None, description="Whether the toon was present at the raid"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about attendance"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or whitespace only")
        return v


class AttendanceResponse(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class AttendanceBulkCreate(BaseModel):
    attendance_records: List[AttendanceCreate] = Field(
        ...,
        description="List of attendance records to create",
        min_length=1,
        max_length=100,  # Limit bulk operations to prevent abuse
    )


class AttendanceBulkUpdate(BaseModel):
    attendance_records: List[dict] = Field(
        ...,
        description="List of attendance records to update. Each record should have 'id' and optional 'is_present' and 'notes' fields",
        min_length=1,
        max_length=100,  # Limit bulk operations to prevent abuse
    )

    @field_validator("attendance_records")
    @classmethod
    def validate_attendance_records(cls, v):
        for record in v:
            if "id" not in record:
                raise ValueError(
                    "Each attendance record must have an 'id' field"
                )
            if (
                "notes" in record
                and record["notes"] is not None
                and record["notes"].strip() == ""
            ):
                raise ValueError("Notes cannot be empty or whitespace only")
        return v


class AttendanceStats(BaseModel):
    total_raids: int = Field(..., description="Total number of raids")
    raids_attended: int = Field(..., description="Number of raids attended")
    raids_missed: int = Field(..., description="Number of raids missed")
    attendance_percentage: float = Field(
        ..., description="Attendance percentage (0.0 to 100.0)"
    )
    current_streak: int = Field(
        ..., description="Current consecutive attendance streak"
    )
    longest_streak: int = Field(
        ..., description="Longest consecutive attendance streak"
    )
    last_attendance: Optional[datetime] = Field(
        None, description="Date of last attendance"
    )


class AttendanceReport(BaseModel):
    start_date: datetime = Field(
        ..., description="Start date for the report period"
    )
    end_date: datetime = Field(
        ..., description="End date for the report period"
    )
    total_raids: int = Field(
        ..., description="Total number of raids in the period"
    )
    total_attendance_records: int = Field(
        ..., description="Total number of attendance records"
    )
    present_count: int = Field(..., description="Number of present records")
    absent_count: int = Field(..., description="Number of absent records")
    overall_attendance_rate: float = Field(
        ..., description="Overall attendance rate for the period"
    )
    attendance_by_raid: List[dict] = Field(
        ..., description="Attendance breakdown by raid"
    )
    attendance_by_toon: List[dict] = Field(
        ..., description="Attendance breakdown by toon"
    )
