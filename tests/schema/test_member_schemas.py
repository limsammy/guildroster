# type: ignore[comparison-overlap,assignment]
"""
Unit tests for Member schemas.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.member import (
    MemberBase,
    MemberCreate,
    MemberUpdate,
    MemberResponse,
)


class TestMemberBase:
    def test_valid_member_base(self):
        """Test creating a valid MemberBase schema."""
        data = {
            "display_name": "Test Member",
            "rank": "Officer",
            "guild_id": 1,
            "team_id": 2,
        }
        member = MemberBase(**data)
        assert member.display_name == "Test Member"
        assert member.rank == "Officer"
        assert member.guild_id == 1
        assert member.team_id == 2

    def test_member_base_without_team(self):
        """Test creating MemberBase without team assignment."""
        data = {
            "display_name": "Test Member",
            "guild_id": 1,
        }
        member = MemberBase(**data)
        assert member.display_name == "Test Member"
        assert member.rank == "Member"  # Default value
        assert member.guild_id == 1
        assert member.team_id is None

    def test_member_base_display_name_too_short(self):
        """Test that display name cannot be empty."""
        data = {
            "display_name": "",
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberBase(**data)
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_member_base_display_name_too_long(self):
        """Test that display name cannot exceed 50 characters."""
        data = {
            "display_name": "A" * 51,  # 51 characters
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberBase(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_member_base_rank_too_long(self):
        """Test that rank cannot exceed 20 characters."""
        data = {
            "display_name": "Test Member",
            "rank": "A" * 21,  # 21 characters
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberBase(**data)
        assert "String should have at most 20 characters" in str(exc_info.value)

    def test_member_base_missing_required_fields(self):
        """Test that required fields are enforced."""
        # Missing display_name
        with pytest.raises(ValidationError):
            MemberBase.model_validate({"guild_id": 1})

        # Missing guild_id
        with pytest.raises(ValidationError):
            MemberBase.model_validate({"display_name": "Test Member"})


class TestMemberCreate:
    def test_valid_member_create(self):
        """Test creating a valid MemberCreate schema."""
        data = {
            "display_name": "Test Member",
            "rank": "Officer",
            "guild_id": 1,
            "team_id": 2,
            "join_date": datetime.now(),
        }
        member = MemberCreate(**data)
        assert member.display_name == "Test Member"
        assert member.rank == "Officer"
        assert member.guild_id == 1
        assert member.team_id == 2
        assert member.join_date is not None

    def test_member_create_without_join_date(self):
        """Test MemberCreate without join_date (should be optional)."""
        data = {
            "display_name": "Test Member",
            "guild_id": 1,
        }
        member = MemberCreate(**data)
        assert member.display_name == "Test Member"
        assert member.join_date is None

    def test_member_create_inherits_validation(self):
        """Test that MemberCreate inherits validation from MemberBase."""
        # Test display name too long
        data = {
            "display_name": "A" * 51,
            "guild_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberCreate(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)


class TestMemberUpdate:
    def test_valid_member_update_all_fields(self):
        """Test updating all fields in MemberUpdate."""
        data = {
            "display_name": "Updated Member Name",
            "rank": "Guild Master",
            "team_id": 3,
            "is_active": False,
        }
        member = MemberUpdate(**data)
        assert member.display_name == "Updated Member Name"
        assert member.rank == "Guild Master"
        assert member.team_id == 3
        assert member.is_active is False

    def test_valid_member_update_partial(self):
        """Test updating only some fields in MemberUpdate."""
        data = {
            "display_name": "Updated Member Name",
        }
        member = MemberUpdate(**data)
        assert member.display_name == "Updated Member Name"
        assert member.rank is None
        assert member.team_id is None
        assert member.is_active is None

    def test_member_update_empty_data(self):
        """Test MemberUpdate with empty data."""
        data = {}
        member = MemberUpdate(**data)
        assert member.display_name is None
        assert member.rank is None
        assert member.team_id is None
        assert member.is_active is None

    def test_member_update_display_name_validation(self):
        """Test that MemberUpdate validates display name length."""
        data = {
            "display_name": "A" * 51,  # Too long
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberUpdate(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_member_update_rank_validation(self):
        """Test that MemberUpdate validates rank length."""
        data = {
            "rank": "A" * 21,  # Too long
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberUpdate(**data)
        assert "String should have at most 20 characters" in str(exc_info.value)


class TestMemberResponse:
    def test_valid_member_response(self):
        """Test creating a valid MemberResponse schema."""
        now = datetime.now()
        data = {
            "id": 1,
            "display_name": "Test Member",
            "rank": "Officer",
            "guild_id": 1,
            "team_id": 2,
            "join_date": now,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        member = MemberResponse(**data)
        assert member.id == 1
        assert member.display_name == "Test Member"
        assert member.rank == "Officer"
        assert member.guild_id == 1
        assert member.team_id == 2
        assert member.join_date == now
        assert member.is_active is True
        assert member.created_at == now
        assert member.updated_at == now

    def test_member_response_missing_required_fields(self):
        """Test that MemberResponse requires all fields."""
        data = {
            "display_name": "Test Member",
            "guild_id": 1,
        }
        with pytest.raises(ValidationError):
            MemberResponse(**data)

    def test_member_response_inherits_validation(self):
        """Test that MemberResponse inherits validation from MemberBase."""
        now = datetime.now()
        data = {
            "id": 1,
            "display_name": "A" * 51,  # Too long
            "guild_id": 1,
            "join_date": now,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberResponse(**data)
        assert "String should have at most 50 characters" in str(exc_info.value)

    def test_member_response_from_orm(self):
        """Test creating MemberResponse from SQLAlchemy model."""

        # Create a mock SQLAlchemy member object
        class MockMember:
            def __init__(self):
                self.id = 1
                self.display_name = "Test Member"
                self.rank = "Officer"
                self.guild_id = 1
                self.team_id = 2
                self.join_date = datetime.now()
                self.is_active = True
                self.created_at = datetime.now()
                self.updated_at = datetime.now()

        mock_member = MockMember()
        member_response = MemberResponse.model_validate(mock_member)
        assert member_response.id == 1
        assert member_response.display_name == "Test Member"
        assert member_response.rank == "Officer"
