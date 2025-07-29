# type: ignore[comparison-overlap,assignment]
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.attendance import (
    AttendanceBase,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBulkCreate,
    AttendanceBulkUpdate,
    AttendanceStats,
    AttendanceReport,
)


class TestAttendanceBase:
    def test_valid_attendance_base(self):
        """Test creating a valid AttendanceBase."""
        data = {
            "raid_id": 1,
            "toon_id": 2,
            "status": "present",
            "notes": "On time and performed well",
        }
        attendance = AttendanceBase(**data)
        assert attendance.raid_id == 1
        assert attendance.toon_id == 2
        assert attendance.status == "present"
        assert attendance.notes == "On time and performed well"

    def test_attendance_base_without_notes(self):
        """Test creating AttendanceBase without notes."""
        data = {"raid_id": 1, "toon_id": 2, "status": "absent"}
        attendance = AttendanceBase(**data)
        assert attendance.notes is None

    def test_attendance_base_empty_notes_validation(self):
        """Test that empty string notes are rejected."""
        data = {"raid_id": 1, "toon_id": 2, "status": "present", "notes": ""}
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBase(**data)
        assert "Notes cannot be empty" in str(exc_info.value)

    def test_attendance_base_whitespace_notes_validation(self):
        """Test that whitespace-only notes are rejected."""
        data = {"raid_id": 1, "toon_id": 2, "status": "present", "notes": "   "}
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBase(**data)
        assert "Notes cannot be empty" in str(exc_info.value)

    def test_attendance_base_notes_length_limit(self):
        """Test that notes respect the 500 character limit."""
        long_notes = "A" * 501
        data = {
            "raid_id": 1,
            "toon_id": 2,
            "status": "present",
            "notes": long_notes,
        }
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBase(**data)
        assert "String should have at most 500 characters" in str(
            exc_info.value
        )

    def test_attendance_base_required_fields(self):
        """Test that required fields are enforced."""
        # Missing raid_id
        with pytest.raises(ValidationError):
            AttendanceBase(toon_id=2, status="present")

        # Missing toon_id
        with pytest.raises(ValidationError):
            AttendanceBase(raid_id=1, status="present")


class TestAttendanceCreate:
    def test_attendance_create_inherits_from_base(self):
        """Test that AttendanceCreate inherits all validation from AttendanceBase."""
        data = {
            "raid_id": 1,
            "toon_id": 2,
            "status": "present",
            "notes": "Test notes",
        }
        attendance = AttendanceCreate(**data)
        assert attendance.raid_id == 1
        assert attendance.toon_id == 2
        assert attendance.status == "present"
        assert attendance.notes == "Test notes"


class TestAttendanceUpdate:
    def test_attendance_update_all_optional(self):
        """Test that all fields in AttendanceUpdate are optional."""
        attendance = AttendanceUpdate()
        assert attendance.status is None
        assert attendance.notes is None

    def test_attendance_update_partial(self):
        """Test updating only some fields."""
        attendance = AttendanceUpdate(is_present=False)
        assert attendance.is_present is False
        assert attendance.notes is None

    def test_attendance_update_notes_validation(self):
        """Test that notes validation still applies in updates."""
        with pytest.raises(ValidationError) as exc_info:
            AttendanceUpdate(notes="")
        assert "Notes cannot be empty" in str(exc_info.value)


class TestAttendanceResponse:
    def test_attendance_response_with_all_fields(self):
        """Test creating AttendanceResponse with all fields."""
        data = {
            "id": 1,
            "raid_id": 2,
            "toon_id": 3,
            "is_present": True,
            "notes": "Test notes",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        attendance = AttendanceResponse(**data)
        assert attendance.id == 1
        assert attendance.raid_id == 2
        assert attendance.toon_id == 3
        assert attendance.is_present is True
        assert attendance.notes == "Test notes"
        assert attendance.created_at is not None
        assert attendance.updated_at is not None


class TestAttendanceBulkCreate:
    def test_valid_bulk_create(self):
        """Test creating valid bulk attendance records."""
        data = {
            "attendance_records": [
                {
                    "raid_id": 1,
                    "toon_id": 2,
                    "is_present": True,
                    "notes": "On time",
                },
                {
                    "raid_id": 1,
                    "toon_id": 3,
                    "is_present": False,
                    "notes": "No show",
                },
            ]
        }
        bulk_create = AttendanceBulkCreate(**data)
        assert len(bulk_create.attendance_records) == 2
        assert bulk_create.attendance_records[0].raid_id == 1
        assert bulk_create.attendance_records[1].toon_id == 3

    def test_bulk_create_empty_list(self):
        """Test that empty list is rejected."""
        data = {"attendance_records": []}
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBulkCreate(**data)
        assert "List should have at least 1 item" in str(exc_info.value)

    def test_bulk_create_too_many_records(self):
        """Test that too many records are rejected."""
        data = {
            "attendance_records": [
                {"raid_id": 1, "toon_id": i, "is_present": True}
                for i in range(101)
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBulkCreate(**data)
        assert "List should have at most 100 items" in str(exc_info.value)

    def test_bulk_create_invalid_record(self):
        """Test that invalid records in bulk create are caught."""
        data = {
            "attendance_records": [
                {
                    "raid_id": 1,
                    "toon_id": 2,
                    "is_present": True,
                    "notes": "",  # Invalid empty notes
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBulkCreate(**data)
        assert "Notes cannot be empty" in str(exc_info.value)


class TestAttendanceBulkUpdate:
    def test_valid_bulk_update(self):
        """Test creating valid bulk update records."""
        data = {
            "attendance_records": [
                {"id": 1, "is_present": False, "notes": "Updated notes"},
                {"id": 2, "is_present": True},
            ]
        }
        bulk_update = AttendanceBulkUpdate(**data)
        assert len(bulk_update.attendance_records) == 2
        assert bulk_update.attendance_records[0].id == 1
        assert bulk_update.attendance_records[1].id == 2

    def test_bulk_update_missing_id(self):
        """Test that missing id field is caught."""
        data = {
            "attendance_records": [
                {"is_present": False, "notes": "No ID field"}
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBulkUpdate(**data)
        assert "Field required" in str(exc_info.value)

    def test_bulk_update_invalid_notes(self):
        """Test that invalid notes in bulk update are caught."""
        data = {
            "attendance_records": [
                {"id": 1, "notes": ""}  # Invalid empty notes
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            AttendanceBulkUpdate(**data)
        assert "Notes cannot be empty" in str(exc_info.value)


class TestAttendanceStats:
    def test_valid_attendance_stats(self):
        """Test creating valid attendance statistics."""
        data = {
            "total_raids": 10,
            "raids_attended": 8,
            "raids_missed": 2,
            "attendance_percentage": 80.0,
            "current_streak": 3,
            "longest_streak": 5,
            "last_attendance": datetime.now(),
        }
        stats = AttendanceStats(**data)
        assert stats.total_raids == 10
        assert stats.raids_attended == 8
        assert stats.raids_missed == 2
        assert stats.attendance_percentage == 80.0
        assert stats.current_streak == 3
        assert stats.longest_streak == 5
        assert stats.last_attendance is not None

    def test_attendance_stats_without_last_attendance(self):
        """Test attendance stats without last attendance date."""
        data = {
            "total_raids": 0,
            "raids_attended": 0,
            "raids_missed": 0,
            "attendance_percentage": 0.0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_attendance": None,
        }
        stats = AttendanceStats(**data)
        assert stats.last_attendance is None


class TestAttendanceReport:
    def test_valid_attendance_report(self):
        """Test creating valid attendance report."""
        data = {
            "start_date": datetime.now(),
            "end_date": datetime.now(),
            "total_raids": 5,
            "total_attendance_records": 25,
            "present_count": 20,
            "absent_count": 5,
            "overall_attendance_rate": 80.0,
            "attendance_by_raid": [{"raid_id": 1, "present": 8, "absent": 2}],
            "attendance_by_toon": [{"toon_id": 1, "present": 4, "absent": 1}],
        }
        report = AttendanceReport(**data)
        assert report.total_raids == 5
        assert report.total_attendance_records == 25
        assert report.present_count == 20
        assert report.absent_count == 5
        assert report.overall_attendance_rate == 80.0
        assert len(report.attendance_by_raid) == 1
        assert len(report.attendance_by_toon) == 1
