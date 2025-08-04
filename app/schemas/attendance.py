from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    BENCHED = "benched"


class AttendanceBase(BaseModel):
    raid_id: int = Field(
        ..., description="Raid ID this attendance record is for"
    )
    toon_id: int = Field(
        ..., description="Toon ID this attendance record is for"
    )
    status: AttendanceStatus = Field(
        AttendanceStatus.PRESENT,
        description="Attendance status: present, absent, or benched",
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about attendance"
    )
    benched_note: Optional[str] = Field(
        None, max_length=500, description="Optional note when status is benched"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or whitespace only")
        return v

    @field_validator("benched_note")
    @classmethod
    def validate_benched_note(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Benched note cannot be empty or whitespace only")
        return v


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = Field(
        None, description="Attendance status: present, absent, or benched"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about attendance"
    )
    benched_note: Optional[str] = Field(
        None, max_length=500, description="Optional note when status is benched"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or whitespace only")
        return v

    @field_validator("benched_note")
    @classmethod
    def validate_benched_note(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Benched note cannot be empty or whitespace only")
        return v


class AttendanceBulkUpdateItem(BaseModel):
    id: int = Field(..., description="Attendance record ID to update")
    status: Optional[AttendanceStatus] = Field(
        None, description="Attendance status: present, absent, or benched"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about attendance"
    )
    benched_note: Optional[str] = Field(
        None, max_length=500, description="Optional note when status is benched"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or whitespace only")
        return v

    @field_validator("benched_note")
    @classmethod
    def validate_benched_note(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Benched note cannot be empty or whitespace only")
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
    attendance_records: List[AttendanceBulkUpdateItem] = Field(
        ...,
        description="List of attendance records to update. Each record should have 'id' and optional 'status', 'notes', and 'benched_note' fields",
        min_length=1,
        max_length=100,  # Limit bulk operations to prevent abuse
    )


class AttendanceStats(BaseModel):
    total_raids: int = Field(..., description="Total number of raids")
    raids_attended: int = Field(..., description="Number of raids attended")
    raids_missed: int = Field(..., description="Number of raids missed")
    raids_benched: int = Field(..., description="Number of raids benched")
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


class BenchedPlayer(BaseModel):
    toon_id: int = Field(..., description="Toon ID")
    toon_name: str = Field(..., description="Toon name")
    class_name: str = Field(..., description="Toon class")
    spec_name: str = Field(..., description="Toon spec")
    raid_id: int = Field(..., description="Raid ID where they were benched")
    raid_name: str = Field(..., description="Raid name")
    raid_date: datetime = Field(..., description="Raid date")
    benched_note: Optional[str] = Field(None, description="Benched note")


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
    benched_count: int = Field(..., description="Number of benched records")
    overall_attendance_rate: float = Field(
        ..., description="Overall attendance rate for the period"
    )
    attendance_by_raid: List[dict] = Field(
        ..., description="Attendance breakdown by raid"
    )
    attendance_by_toon: List[dict] = Field(
        ..., description="Attendance breakdown by toon"
    )


# New schemas for team view
class ToonAttendanceRecord(BaseModel):
    raid_id: int = Field(..., description="Raid ID")
    raid_date: datetime = Field(..., description="Raid date")
    status: AttendanceStatus = Field(..., description="Attendance status")
    notes: Optional[str] = Field(None, description="Attendance notes")
    benched_note: Optional[str] = Field(None, description="Benched note")
    has_note: bool = Field(..., description="Whether this record has any notes")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TeamViewToon(BaseModel):
    id: int = Field(..., description="Toon ID")
    username: str = Field(..., description="Toon username")
    class_name: str = Field(..., description="Toon class")
    role: str = Field(..., description="Toon role")
    overall_attendance_percentage: float = Field(..., description="Overall attendance percentage")
    attendance_records: List[ToonAttendanceRecord] = Field(..., description="Attendance records for this toon")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TeamViewRaid(BaseModel):
    id: int = Field(..., description="Raid ID")
    scheduled_at: datetime = Field(..., description="Raid scheduled date")
    scenario_name: str = Field(..., description="Scenario name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TeamViewData(BaseModel):
    team: dict = Field(..., description="Team information")
    toons: List[TeamViewToon] = Field(..., description="Toons with their attendance data")
    raids: List[TeamViewRaid] = Field(..., description="Raids included in this view")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
