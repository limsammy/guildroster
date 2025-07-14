# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.scenario import Scenario
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team

from app.models.raid import Raid


class TestScenarioModel:
    def setup_user(self, db_session: Session):
        """Helper method to create a user."""
        user = User(
            username="testuser",
            hashed_password="hashedpassword",
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        return user

    def setup_guild(self, db_session: Session, user_id: int):
        """Helper method to create a guild."""
        guild = Guild(name="Test Guild", created_by=user_id)
        db_session.add(guild)
        db_session.commit()
        return guild

    def setup_team(self, db_session: Session, guild_id: int, user_id: int):
        """Helper method to create a team."""
        team = Team(
            name="Test Team",
            guild_id=guild_id,
            created_by=user_id,
        )
        db_session.add(team)
        db_session.commit()
        return team

    def test_create_scenario(self, db_session: Session):
        """Test creating a scenario with valid data."""
        scenario = Scenario(name="Blackrock Foundry")
        db_session.add(scenario)
        db_session.commit()

        assert scenario.id is not None
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True
        assert scenario.created_at is not None
        assert scenario.updated_at is not None

    def test_scenario_name_unique_constraint(self, db_session: Session):
        """Test that scenario names must be unique."""
        scenario1 = Scenario(name="Blackrock Foundry")
        db_session.add(scenario1)
        db_session.commit()

        scenario2 = Scenario(name="Blackrock Foundry")
        db_session.add(scenario2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scenario_name_not_empty_constraint(self, db_session: Session):
        """Test that scenario names cannot be empty."""
        scenario = Scenario(name="")
        db_session.add(scenario)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scenario_name_whitespace_only_constraint(
        self, db_session: Session
    ):
        """Test that scenario names cannot be whitespace only."""
        scenario = Scenario(name="   ")
        db_session.add(scenario)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scenario_is_active_default(self, db_session: Session):
        """Test that is_active defaults to True."""
        scenario = Scenario(name="Test Scenario")
        db_session.add(scenario)
        db_session.commit()

        assert scenario.is_active is True

    def test_scenario_is_active_can_be_false(self, db_session: Session):
        """Test that is_active can be set to False."""
        scenario = Scenario(name="Test Scenario", is_active=False)
        db_session.add(scenario)
        db_session.commit()

        assert scenario.is_active is False

    def test_scenario_relationship_to_raids(self, db_session: Session):
        """Test relationship between scenario and raids."""
        user = self.setup_user(db_session)
        user_id = user.id  # Store ID before making API request
        guild = self.setup_guild(db_session, user_id)
        guild_id = guild.id  # Store ID before making API request
        team = self.setup_team(db_session, guild_id, user_id)
        team_id = team.id  # Store ID before making API request

        scenario = Scenario(name="Test Scenario")
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id  # Store ID before making API request

        from datetime import datetime, timedelta

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
            scenario_id=scenario_id,
        )
        db_session.add(raid)
        db_session.commit()

        assert raid in scenario.raids
        assert raid.scenario == scenario

    def test_cascade_delete_on_scenario(self, db_session: Session):
        """Test that deleting a scenario cascades to raids."""
        user = self.setup_user(db_session)
        user_id = user.id  # Store ID before making API request
        guild = self.setup_guild(db_session, user_id)
        guild_id = guild.id  # Store ID before making API request
        team = self.setup_team(db_session, guild_id, user_id)
        team_id = team.id  # Store ID before making API request

        scenario = Scenario(name="Test Scenario")
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id  # Store ID before making API request

        from datetime import datetime, timedelta

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
            scenario_id=scenario_id,
        )
        db_session.add(raid)
        db_session.commit()

        raid_id = raid.id
        db_session.delete(scenario)
        db_session.commit()

        deleted_raid = db_session.query(Raid).filter(Raid.id == raid_id).first()
        assert deleted_raid is None

    def test_scenario_timestamps(self, db_session: Session):
        """Test that created_at and updated_at are set correctly."""
        scenario = Scenario(name="Test Scenario")
        db_session.add(scenario)
        db_session.commit()

        original_created_at = scenario.created_at
        original_updated_at = scenario.updated_at

        # Update the scenario
        scenario.name = "Updated Scenario"  # type: ignore[assignment]
        db_session.commit()

        assert scenario.created_at == original_created_at
        assert scenario.updated_at > original_updated_at
