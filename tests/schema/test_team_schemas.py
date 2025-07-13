"""
Unit tests for Team schemas.
"""

import pytest
from pydantic import ValidationError
from app.schemas.team import TeamBase, TeamCreate, TeamUpdate, TeamResponse


class TestTeamBase:
    def test_valid_team_base(self):
        """Test creating a valid TeamBase schema."""
        data = {
            "name": "Raid Team A",
            "description": "Main raid team",
            "guild_id": 1,
        }
        team = TeamBase(**data)
        assert team.name == "Raid Team A"
        assert team.description == "Main raid team"
        assert team.guild_id == 1

    def test_team_base_without_description(self):
        """Test creating TeamBase without description."""
        data = {
            "name": "PvP Team",
            "guild_id": 1,
        }
        team = TeamBase(**data)
        assert team.name == "PvP Team"
        assert team.description is None
        assert team.guild_id == 1

    def test_team_base_name_too_short(self):
        """Test that team name cannot be empty."""
        data = {
            "name": "",
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**data)
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_team_base_name_too_long(self):
        """Test that team name cannot exceed 50 characters."""
        data = {
            "name": "A" * 51,  # 51 characters
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_team_base_description_too_long(self):
        """Test that description cannot exceed 200 characters."""
        data = {
            "name": "Test Team",
            "description": "A" * 201,  # 201 characters
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**data)
        assert "String should have at most 200 characters" in str(
            exc_info.value
        )

    def test_team_base_missing_required_fields(self):
        """Test that required fields are enforced."""
        # Missing name
        with pytest.raises(ValidationError):
            TeamBase.model_validate({"guild_id": 1})

        # Missing guild_id
        with pytest.raises(ValidationError):
            TeamBase.model_validate({"name": "Test Team"})


class TestTeamCreate:
    def test_valid_team_create(self):
        """Test creating a valid TeamCreate schema."""
        data = {
            "name": "Raid Team A",
            "description": "Main raid team",
            "guild_id": 1,
            "created_by": 1,
        }
        team = TeamCreate(**data)
        assert team.name == "Raid Team A"
        assert team.description == "Main raid team"
        assert team.guild_id == 1
        assert team.created_by == 1

    def test_team_create_missing_created_by(self):
        """Test that created_by is required."""
        data = {
            "name": "Test Team",
            "guild_id": 1,
        }
        with pytest.raises(ValidationError):
            TeamCreate(**data)

    def test_team_create_inherits_validation(self):
        """Test that TeamCreate inherits validation from TeamBase."""
        # Test name too long
        data = {
            "name": "A" * 51,
            "guild_id": 1,
            "created_by": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamCreate(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)


class TestTeamUpdate:
    def test_valid_team_update_all_fields(self):
        """Test updating all fields in TeamUpdate."""
        data = {
            "name": "Updated Team Name",
            "description": "Updated description",
            "is_active": False,
        }
        team = TeamUpdate(**data)
        assert team.name == "Updated Team Name"
        assert team.description == "Updated description"
        assert team.is_active is False

    def test_valid_team_update_partial(self):
        """Test updating only some fields in TeamUpdate."""
        data = {
            "name": "Updated Team Name",
        }
        team = TeamUpdate(**data)
        assert team.name == "Updated Team Name"
        assert team.description is None
        assert team.is_active is None

    def test_team_update_empty_data(self):
        """Test TeamUpdate with empty data."""
        data = {}
        team = TeamUpdate(**data)
        assert team.name is None
        assert team.description is None
        assert team.is_active is None

    def test_team_update_name_validation(self):
        """Test that TeamUpdate validates name length."""
        data = {
            "name": "A" * 51,  # Too long
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamUpdate(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_team_update_description_validation(self):
        """Test that TeamUpdate validates description length."""
        data = {
            "description": "A" * 201,  # Too long
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamUpdate(**data)
        assert "String should have at most 200 characters" in str(
            exc_info.value
        )


class TestTeamResponse:
    def test_valid_team_response(self):
        """Test creating a valid TeamResponse schema."""
        from datetime import datetime

        now = datetime.now()
        data = {
            "id": 1,
            "name": "Raid Team A",
            "description": "Main raid team",
            "guild_id": 1,
            "created_by": 1,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        team = TeamResponse(**data)
        assert team.id == 1
        assert team.name == "Raid Team A"
        assert team.description == "Main raid team"
        assert team.guild_id == 1
        assert team.created_by == 1
        assert team.is_active is True
        assert team.created_at == now
        assert team.updated_at == now

    def test_team_response_missing_required_fields(self):
        """Test that TeamResponse requires all fields."""
        data = {
            "name": "Test Team",
            "guild_id": 1,
        }
        with pytest.raises(ValidationError):
            TeamResponse(**data)

    def test_team_response_inherits_validation(self):
        """Test that TeamResponse inherits validation from TeamBase."""
        from datetime import datetime

        now = datetime.now()
        data = {
            "id": 1,
            "name": "A" * 51,  # Too long
            "guild_id": 1,
            "created_by": 1,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamResponse(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_team_response_from_orm(self):
        """Test that TeamResponse can be created from ORM model attributes."""
        from datetime import datetime

        # Simulate ORM model attributes
        class MockTeam:
            def __init__(self):
                self.id = 1
                self.name = "Test Team"
                self.description = "Test description"
                self.guild_id = 1
                self.created_by = 1
                self.is_active = True
                self.created_at = datetime.now()
                self.updated_at = datetime.now()

        mock_team = MockTeam()
        team_response = TeamResponse.model_validate(mock_team)

        assert team_response.id == 1
        assert team_response.name == "Test Team"
        assert team_response.description == "Test description"
        assert team_response.guild_id == 1
        assert team_response.created_by == 1
        assert team_response.is_active is True
