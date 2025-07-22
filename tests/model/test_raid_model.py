# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.raid import Raid
from app.models.scenario import Scenario, SCENARIO_DIFFICULTIES, SCENARIO_SIZES
from app.models.team import Team
from app.models.guild import Guild
from app.models.user import User


class TestRaidModel:
    def setup_raid_dependencies(self, db_session: Session):
        """Helper method to create dependencies for raid testing."""
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
        scenario = Scenario(
            name="Test Scenario",
            difficulty=SCENARIO_DIFFICULTIES[0],
            size=SCENARIO_SIZES[0],
            is_active=True,
        )
        db_session.add(scenario)
        db_session.commit()

        return team, scenario

    def test_create_raid(self, db_session: Session):
        """Test creating a basic raid."""
        team, scenario = self.setup_raid_dependencies(db_session)

        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            team_id=team.id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test",
        )
        db_session.add(raid)
        db_session.commit()

        assert raid.id is not None
        assert raid.scheduled_at > datetime.now()
        assert raid.scenario_id == scenario.id
        assert raid.team_id == team.id
        assert (
            raid.warcraftlogs_url == "https://www.warcraftlogs.com/reports/test"
        )

    def test_create_raid_with_warcraftlogs_data(self, db_session: Session):
        """Test creating a raid with WarcraftLogs JSON data."""
        team, scenario = self.setup_raid_dependencies(db_session)

        warcraftlogs_metadata = {
            "title": "Test Raid",
            "startTime": 1234567890,
            "endTime": 1234567890,
            "owner": {"name": "Test Owner"},
            "zone": {"name": "Test Zone"},
        }

        warcraftlogs_participants = [
            {
                "id": 123,
                "canonicalID": 123,
                "name": "TestPlayer1",
                "classID": 11,
                "class": "Druid",
            }
        ]

        warcraftlogs_fights = [
            {
                "id": 1,
                "name": "Test Boss",
                "startTime": 1234567890,
                "endTime": 1234567890,
                "difficulty": "Mythic",
                "kill": True,
            }
        ]

        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            team_id=team.id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/abc123def456",
            warcraftlogs_report_code="abc123def456",
            warcraftlogs_metadata=warcraftlogs_metadata,
            warcraftlogs_participants=warcraftlogs_participants,
            warcraftlogs_fights=warcraftlogs_fights,
        )
        db_session.add(raid)
        db_session.commit()

        assert raid.id is not None
        assert raid.warcraftlogs_report_code == "abc123def456"
        assert raid.warcraftlogs_metadata == warcraftlogs_metadata
        assert raid.warcraftlogs_participants == warcraftlogs_participants
        assert raid.warcraftlogs_fights == warcraftlogs_fights

    def test_raid_json_field_storage(self, db_session: Session):
        """Test that JSON fields can store and retrieve complex data."""
        team, scenario = self.setup_raid_dependencies(db_session)

        complex_metadata = {
            "title": "Complex Raid",
            "nested": {
                "data": {
                    "participants": [
                        {"name": "Player1", "class": "Mage"},
                        {"name": "Player2", "class": "Warrior"},
                    ]
                }
            },
            "arrays": [1, 2, 3, {"nested": "value"}],
        }

        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            team_id=team.id,
            warcraftlogs_metadata=complex_metadata,
        )
        db_session.add(raid)
        db_session.commit()

        # Refresh from database to ensure JSON was stored correctly
        db_session.refresh(raid)
        assert raid.warcraftlogs_metadata == complex_metadata
        assert (
            raid.warcraftlogs_metadata["nested"]["data"]["participants"][0][
                "name"
            ]
            == "Player1"
        )
