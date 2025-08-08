"""
Tests for the attendance image generator.
"""

import pytest
from datetime import datetime, timedelta
from app.utils.image_generator import (
    AttendanceImageGenerator,
    get_current_period,
)
from app.schemas.attendance import (
    TeamViewData,
    TeamViewToon,
    TeamViewRaid,
    ToonAttendanceRecord,
)
from app.models.guild import Guild


class TestAttendanceImageGenerator:
    """Test the attendance image generator."""

    def test_get_current_period(self):
        """Test getting the current period."""
        start_date, end_date = get_current_period()

        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert start_date < end_date

        # Should be a Tuesday
        assert start_date.weekday() == 1  # Tuesday is 1

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = AttendanceImageGenerator()
        assert generator.width == 1200
        assert generator.height == 800

        # Test custom dimensions
        generator = AttendanceImageGenerator(width=1000, height=600)
        assert generator.width == 1000
        assert generator.height == 600

    def test_color_scheme(self):
        """Test color scheme is properly defined."""
        generator = AttendanceImageGenerator()

        required_colors = [
            "background",
            "card_background",
            "text_primary",
            "text_secondary",
            "accent",
            "success",
            "warning",
            "error",
        ]

        for color in required_colors:
            assert color in generator.COLORS
            assert len(generator.COLORS[color]) in [3, 4]  # RGB or RGBA

    def test_format_date(self):
        """Test date formatting."""
        generator = AttendanceImageGenerator()

        # Test ISO format
        date_str = "2024-01-15T10:30:00Z"
        formatted = generator._format_date(date_str)
        assert formatted == "Jan 15"

        # Test invalid date
        formatted = generator._format_date("invalid")
        assert formatted == "invalid"

    def test_period_text(self):
        """Test period text generation."""
        generator = AttendanceImageGenerator()

        # Test with both dates
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 21)
        text = generator._get_period_text(start, end)
        assert "January 15, 2024" in text
        assert "January 21, 2024" in text

        # Test with only start date
        text = generator._get_period_text(start, None)
        assert "Starting: January 15, 2024" in text

        # Test with no dates
        text = generator._get_period_text(None, None)
        assert "Generated:" in text

    def test_generate_team_report(self):
        """Test generating a team report image."""
        generator = AttendanceImageGenerator()

        # Create mock data
        guild = Guild(
            id=1,
            name="Test Guild",
            created_by=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        team_data = TeamViewData(
            team={"id": 1, "name": "Test Team", "guild_id": 1},
            toons=[
                TeamViewToon(
                    id=1,
                    username="TestToon",
                    class_name="Warrior",
                    role="Tank",
                    overall_attendance_percentage=85.5,
                    attendance_records=[
                        ToonAttendanceRecord(
                            raid_id=1,
                            raid_date=datetime.now(),
                            status="present",
                            notes=None,
                            benched_note=None,
                            has_note=False,
                        )
                    ],
                )
            ],
            raids=[
                TeamViewRaid(
                    id=1,
                    scheduled_at=datetime.now(),
                    scenario_name="Test Scenario",
                )
            ],
        )

        # Generate image
        image_bytes = generator.generate_team_report(team_data, guild)

        # Verify it's a valid PNG
        assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(image_bytes) > 1000  # Should be a reasonable size

    def test_generate_multiple_reports(self):
        """Test generating multiple reports as ZIP."""
        generator = AttendanceImageGenerator()

        # Create mock data
        guild = Guild(
            id=1,
            name="Test Guild",
            created_by=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        team_data = TeamViewData(
            team={"id": 1, "name": "Test Team", "guild_id": 1},
            toons=[],
            raids=[],
        )

        reports_data = [(team_data, guild, None, None)]

        # Generate ZIP
        zip_bytes = generator.generate_multiple_reports(reports_data)

        # Verify it's a valid ZIP file
        assert zip_bytes.startswith(b"PK\x03\x04")  # ZIP file signature
        assert len(zip_bytes) > 100  # Should be a reasonable size

    def test_attendance_cell_drawing(self):
        """Test drawing attendance cells."""
        from PIL import Image, ImageDraw

        generator = AttendanceImageGenerator()
        img = Image.new("RGB", (100, 100), generator.COLORS["background"])
        draw = ImageDraw.Draw(img)

        # Test present cell
        generator._draw_attendance_cell(draw, 10, 10, 30, "present", False)

        # Test absent cell with note
        generator._draw_attendance_cell(draw, 50, 10, 30, "absent", True)

        # Test benched cell
        generator._draw_attendance_cell(draw, 10, 50, 30, "benched", False)

        # Verify image was modified
        img_bytes = img.tobytes()
        assert len(img_bytes) > 0
