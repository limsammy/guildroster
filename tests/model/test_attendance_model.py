# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.attendance import Attendance
from app.models.raid import Raid, RAID_DIFFICULTIES, RAID_SIZES
from app.models.toon import Toon, WOW_CLASSES, WOW_ROLES
from app.models.member import Member
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.scenario import Scenario


class TestAttendanceModel:
    def setup_raid_and_toon(self, db_session: Session):
        """Helper method to create a raid and toon for testing."""
        # Create user
        user = User(username="testuser", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()

        # Create guild
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(name="Test Team", guild_id=guild.id, created_by=user.id)
        db_session.add(team)
        db_session.commit()

        # Create scenario
        scenario = Scenario(name="Test Scenario", is_active=True)
        db_session.add(scenario)
        db_session.commit()

        # Create member
        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        # Create toon
        toon = Toon(
            member_id=member.id, username="TestToon", class_="Mage", role="DPS"
        )
        db_session.add(toon)
        db_session.commit()

        # Create raid
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            difficulty=RAID_DIFFICULTIES[0],
            size=RAID_SIZES[0],
            team_id=team.id,
        )
        db_session.add(raid)
        db_session.commit()

        return raid, toon

    def test_create_attendance(self, db_session: Session):
        """Test creating a basic attendance record."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id,
            toon_id=toon.id,
            is_present=True,
            notes="On time and performed well",
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.id is not None
        assert attendance.raid_id == raid.id
        assert attendance.toon_id == toon.id
        assert attendance.is_present is True
        assert attendance.notes == "On time and performed well"
        assert attendance.created_at is not None
        assert attendance.updated_at is not None

    def test_create_attendance_without_notes(self, db_session: Session):
        """Test creating attendance record without notes."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=False
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.id is not None
        assert attendance.notes is None
        assert attendance.is_present is False

    def test_unique_raid_toon_constraint(self, db_session: Session):
        """Test that duplicate attendance records are prevented."""
        raid, toon = self.setup_raid_and_toon(db_session)

        # Create first attendance record
        attendance1 = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance1)
        db_session.commit()

        # Try to create duplicate attendance record
        attendance2 = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=False
        )
        db_session.add(attendance2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_notes_not_empty_constraint(self, db_session: Session):
        """Test that empty string notes are not allowed."""
        raid, toon = self.setup_raid_and_toon(db_session)

        # Test with empty string notes
        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True, notes=""
        )
        db_session.add(attendance)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

        # Test with whitespace-only notes
        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True, notes="   "
        )
        db_session.add(attendance)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_relationship_to_raid(self, db_session: Session):
        """Test relationship between attendance and raid."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.raid == raid
        assert attendance in raid.attendance

    def test_relationship_to_toon(self, db_session: Session):
        """Test relationship between attendance and toon."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.toon == toon
        assert attendance in toon.attendance

    def test_cascade_delete_on_raid(self, db_session: Session):
        """Test that attendance records are deleted when raid is deleted."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance)
        db_session.commit()

        attendance_id = attendance.id
        db_session.delete(raid)
        db_session.commit()

        deleted = (
            db_session.query(Attendance)
            .filter(Attendance.id == attendance_id)
            .first()
        )
        assert deleted is None

    def test_cascade_delete_on_toon(self, db_session: Session):
        """Test that attendance records are deleted when toon is deleted."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance)
        db_session.commit()

        attendance_id = attendance.id
        db_session.delete(toon)
        db_session.commit()

        deleted = (
            db_session.query(Attendance)
            .filter(Attendance.id == attendance_id)
            .first()
        )
        assert deleted is None

    def test_foreign_key_constraint_raid(self, db_session: Session):
        """Test that invalid raid_id raises IntegrityError."""
        _, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=99999, toon_id=toon.id, is_present=True  # Non-existent raid
        )
        db_session.add(attendance)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_foreign_key_constraint_toon(self, db_session: Session):
        """Test that invalid toon_id raises IntegrityError."""
        raid, _ = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=99999, is_present=True  # Non-existent toon
        )
        db_session.add(attendance)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_timestamps(self, db_session: Session):
        """Test that timestamps are properly set and updated."""
        raid, toon = self.setup_raid_and_toon(db_session)

        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance)
        db_session.commit()

        created_at = attendance.created_at
        updated_at = attendance.updated_at

        # Update the attendance record
        attendance.notes = "Updated notes"
        db_session.commit()

        assert attendance.created_at == created_at
        assert attendance.updated_at >= updated_at

    def test_multiple_attendance_records(self, db_session: Session):
        """Test creating multiple attendance records for different raids/toons."""
        raid1, toon1 = self.setup_raid_and_toon(db_session)

        # Create second toon
        user = db_session.query(User).first()
        guild = db_session.query(Guild).first()
        member2 = Member(guild_id=guild.id, display_name="Test Member 2")
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()

        # Create second raid
        scenario = db_session.query(Scenario).first()
        team = db_session.query(Team).first()
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=scenario.id,
            difficulty=RAID_DIFFICULTIES[1],
            size=RAID_SIZES[1],
            team_id=team.id,
        )
        db_session.add(raid2)
        db_session.commit()

        # Create multiple attendance records
        attendance1 = Attendance(
            raid_id=raid1.id, toon_id=toon1.id, is_present=True
        )
        attendance2 = Attendance(
            raid_id=raid1.id, toon_id=toon2.id, is_present=False
        )
        attendance3 = Attendance(
            raid_id=raid2.id, toon_id=toon1.id, is_present=True
        )
        attendance4 = Attendance(
            raid_id=raid2.id, toon_id=toon2.id, is_present=True
        )

        db_session.add_all([attendance1, attendance2, attendance3, attendance4])
        db_session.commit()

        # Verify all records were created
        assert len(raid1.attendance) == 2
        assert len(raid2.attendance) == 2
        assert len(toon1.attendance) == 2
        assert len(toon2.attendance) == 2

    def test_boolean_is_present_field(self, db_session: Session):
        """Test the is_present boolean field with different values."""
        raid, toon = self.setup_raid_and_toon(db_session)

        # Test with True
        attendance_true = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True
        )
        db_session.add(attendance_true)
        db_session.commit()
        assert attendance_true.is_present is True

        # Test with False
        attendance_false = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=False
        )
        db_session.add(attendance_false)
        with pytest.raises(
            IntegrityError
        ):  # Should fail due to unique constraint
            db_session.commit()
        db_session.rollback()

    def test_notes_length_limit(self, db_session: Session):
        """Test that notes can handle long strings within the 500 character limit."""
        raid, toon = self.setup_raid_and_toon(db_session)

        # Test with maximum length notes
        long_notes = "A" * 500
        attendance = Attendance(
            raid_id=raid.id, toon_id=toon.id, is_present=True, notes=long_notes
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.notes == long_notes
        assert len(attendance.notes) == 500
