# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.scenario import Scenario, SCENARIO_DIFFICULTIES, SCENARIO_SIZES
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team


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
        """Test creating a scenario template with valid data."""
        scenario = Scenario(
            name="Blackrock Foundry",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()

        assert scenario.id is not None
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True
        assert scenario.mop is False
        assert scenario.created_at is not None
        assert scenario.updated_at is not None

    def test_create_mop_scenario(self, db_session: Session):
        """Test creating a MoP scenario template."""
        scenario = Scenario(
            name="Mogu'shan Vaults",
            is_active=True,
            mop=True,
        )
        db_session.add(scenario)
        db_session.commit()

        assert scenario.id is not None
        assert scenario.name == "Mogu'shan Vaults"
        assert scenario.is_active is True
        assert scenario.mop is True

    def test_scenario_name_not_empty_constraint(self, db_session: Session):
        """Test that scenario names cannot be empty."""
        scenario = Scenario(
            name="",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scenario_name_whitespace_only_constraint(
        self, db_session: Session
    ):
        """Test that scenario names cannot be whitespace only."""
        scenario = Scenario(
            name="   ",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scenario_is_active_default(self, db_session: Session):
        """Test that is_active defaults to True."""
        scenario = Scenario(
            name="Test Scenario",
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()

        assert scenario.is_active is True

    def test_scenario_mop_default(self, db_session: Session):
        """Test that mop defaults to False."""
        scenario = Scenario(
            name="Test Scenario",
            is_active=True,
        )
        db_session.add(scenario)
        db_session.commit()

        assert scenario.mop is False

    def test_scenario_is_active_can_be_false(self, db_session: Session):
        """Test that is_active can be set to False."""
        scenario = Scenario(
            name="Test Scenario",
            is_active=False,
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()

        assert scenario.is_active is False

    def test_get_variations_non_mop(self, db_session: Session):
        """Test that non-MoP scenarios generate 4 variations."""
        scenario = Scenario(
            name="Molten Core",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()

        variations = Scenario.get_variations(scenario.name, scenario.mop)

        assert len(variations) == 4
        # Check that only Normal and Heroic difficulties are included
        difficulties = {var["difficulty"] for var in variations}
        assert difficulties == {"Normal", "Heroic"}
        # Check that both sizes are included
        sizes = {var["size"] for var in variations}
        assert sizes == {"10", "25"}

    def test_get_variations_mop(self, db_session: Session):
        """Test that MoP scenarios generate 8 variations."""
        scenario = Scenario(
            name="Mogu'shan Vaults",
            is_active=True,
            mop=True,
        )
        db_session.add(scenario)
        db_session.commit()

        variations = Scenario.get_variations(scenario.name, scenario.mop)

        assert len(variations) == 8
        # Check that all difficulties are included
        difficulties = {var["difficulty"] for var in variations}
        assert difficulties == set(SCENARIO_DIFFICULTIES)
        # Check that both sizes are included
        sizes = {var["size"] for var in variations}
        assert sizes == {"10", "25"}

    def test_get_variation_id(self, db_session: Session):
        """Test variation ID generation."""
        variation_id = Scenario.get_variation_id("Molten Core", "Normal", "10")
        assert variation_id == "Molten Core|Normal|10"

    def test_parse_variation_id(self, db_session: Session):
        """Test variation ID parsing."""
        parsed = Scenario.parse_variation_id("Molten Core|Normal|10")
        assert parsed == {
            "name": "Molten Core",
            "difficulty": "Normal",
            "size": "10",
        }

    def test_parse_variation_id_invalid(self, db_session: Session):
        """Test that invalid variation IDs raise an error."""
        with pytest.raises(ValueError, match="Invalid variation ID format"):
            Scenario.parse_variation_id("invalid_format")

    def test_scenario_timestamps(self, db_session: Session):
        """Test that created_at and updated_at are set correctly."""
        scenario = Scenario(
            name="Test Scenario",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()

        original_created_at = scenario.created_at
        original_updated_at = scenario.updated_at

        # Update the scenario
        scenario.name = "Updated Scenario"  # type: ignore[assignment]
        db_session.commit()

        assert scenario.created_at == original_created_at
        assert scenario.updated_at > original_updated_at
