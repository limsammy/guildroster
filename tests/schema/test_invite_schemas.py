# type: ignore[comparison-overlap,assignment,arg-type]
"""
Schema tests for invite-related Pydantic models.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.schemas.invite import (
    InviteBase,
    InviteCreate,
    InviteResponse,
    InviteListResponse,
)
from app.schemas.user import UserRegistration


class TestInviteBase:
    def test_invite_base_valid(self):
        """Test valid InviteBase creation."""
        data = {
            "code": "ABC12345",
            "is_active": True,
            "expires_at": datetime.now() + timedelta(days=7),
        }

        invite = InviteBase(**data)
        assert invite.code == "ABC12345"
        assert invite.is_active is True
        assert invite.expires_at is not None

    def test_invite_base_no_expiration(self):
        """Test InviteBase with no expiration."""
        data = {"code": "ABC12345", "is_active": True, "expires_at": None}

        invite = InviteBase(**data)
        assert invite.code == "ABC12345"
        assert invite.is_active is True
        assert invite.expires_at is None

    def test_invite_base_missing_fields(self):
        """Test InviteBase with missing required fields."""
        # Missing code
        with pytest.raises(ValidationError) as exc_info:
            InviteBase(is_active=True, expires_at=None)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("code",)
        assert errors[0]["type"] == "missing"

        # Missing is_active
        with pytest.raises(ValidationError) as exc_info:
            InviteBase(code="ABC12345", expires_at=None)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("is_active",)
        assert errors[0]["type"] == "missing"


class TestInviteCreate:
    def test_invite_create_default(self):
        """Test InviteCreate with default values."""
        invite = InviteCreate()
        assert invite.expires_in_days == 7

    def test_invite_create_custom_expiration(self):
        """Test InviteCreate with custom expiration."""
        invite = InviteCreate(expires_in_days=30)
        assert invite.expires_in_days == 30

    def test_invite_create_no_expiration(self):
        """Test InviteCreate with no expiration."""
        invite = InviteCreate(expires_in_days=None)
        assert invite.expires_in_days is None

    def test_invite_create_invalid_expiration_too_short(self):
        """Test InviteCreate with expiration too short."""
        with pytest.raises(ValidationError) as exc_info:
            InviteCreate(expires_in_days=0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("expires_in_days",)
        assert "greater than or equal to 1" in errors[0]["msg"]

    def test_invite_create_invalid_expiration_too_long(self):
        """Test InviteCreate with expiration too long."""
        with pytest.raises(ValidationError) as exc_info:
            InviteCreate(expires_in_days=366)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("expires_in_days",)
        assert "less than or equal to 365" in errors[0]["msg"]


class TestInviteResponse:
    def test_invite_response_valid(self):
        """Test valid InviteResponse creation."""
        now = datetime.now()
        data = {
            "id": 1,
            "code": "ABC12345",
            "created_by": 2,
            "used_by": 3,
            "is_active": True,
            "expires_at": now + timedelta(days=7),
            "created_at": now,
            "used_at": now,
            "creator_username": "creator",
            "used_username": "user",
            "is_expired": False,
        }

        invite = InviteResponse(**data)
        assert invite.id == 1
        assert invite.code == "ABC12345"
        assert invite.created_by == 2
        assert invite.used_by == 3
        assert invite.is_active is True
        assert invite.creator_username == "creator"
        assert invite.used_username == "user"
        assert invite.is_expired is False

    def test_invite_response_unused(self):
        """Test InviteResponse for unused invite."""
        now = datetime.now()
        data = {
            "id": 1,
            "code": "ABC12345",
            "created_by": 2,
            "used_by": None,
            "is_active": True,
            "expires_at": now + timedelta(days=7),
            "created_at": now,
            "used_at": None,
            "creator_username": "creator",
            "used_username": None,
            "is_expired": False,
        }

        invite = InviteResponse(**data)
        assert invite.used_by is None
        assert invite.used_at is None
        assert invite.used_username is None

    def test_invite_response_expired(self):
        """Test InviteResponse for expired invite."""
        now = datetime.now()
        data = {
            "id": 1,
            "code": "ABC12345",
            "created_by": 2,
            "used_by": None,
            "is_active": True,
            "expires_at": now - timedelta(days=1),
            "created_at": now,
            "used_at": None,
            "creator_username": "creator",
            "used_username": None,
            "is_expired": True,
        }

        invite = InviteResponse(**data)
        assert invite.is_expired is True

    def test_invite_response_missing_required_fields(self):
        """Test InviteResponse with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            InviteResponse(code="ABC12345", is_active=True, expires_at=None)

        errors = exc_info.value.errors()
        # Should have multiple missing field errors
        assert len(errors) > 1


class TestInviteListResponse:
    def test_invite_list_response_valid(self):
        """Test valid InviteListResponse creation."""
        now = datetime.now()
        invites = [
            {
                "id": 1,
                "code": "ABC12345",
                "created_by": 2,
                "used_by": None,
                "is_active": True,
                "expires_at": now + timedelta(days=7),
                "created_at": now,
                "used_at": None,
                "creator_username": "creator",
                "used_username": None,
                "is_expired": False,
            }
        ]

        data = {
            "invites": invites,
            "total": 1,
            "unused_count": 1,
            "used_count": 0,
            "expired_count": 0,
        }

        response = InviteListResponse(**data)
        assert len(response.invites) == 1
        assert response.total == 1
        assert response.unused_count == 1
        assert response.used_count == 0
        assert response.expired_count == 0

    def test_invite_list_response_empty(self):
        """Test InviteListResponse with empty list."""
        data = {
            "invites": [],
            "total": 0,
            "unused_count": 0,
            "used_count": 0,
            "expired_count": 0,
        }

        response = InviteListResponse(**data)
        assert len(response.invites) == 0
        assert response.total == 0

    def test_invite_list_response_missing_fields(self):
        """Test InviteListResponse with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            InviteListResponse(invites=[])

        errors = exc_info.value.errors()
        # Should have multiple missing field errors
        assert len(errors) > 1


class TestUserRegistration:
    def test_user_registration_valid(self):
        """Test valid UserRegistration creation."""
        data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        registration = UserRegistration(**data)
        assert registration.username == "newuser"
        assert registration.password == "newpassword123"
        assert registration.invite_code == "ABC12345"

    def test_user_registration_invalid_username_too_short(self):
        """Test UserRegistration with username too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="ab", password="newpassword123", invite_code="ABC12345"
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("username",)
        assert "at least 3 characters" in errors[0]["msg"]

    def test_user_registration_invalid_username_too_long(self):
        """Test UserRegistration with username too long."""
        long_username = "a" * 51  # 51 characters
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username=long_username,
                password="newpassword123",
                invite_code="ABC12345",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("username",)
        assert "at most 50 characters" in errors[0]["msg"]

    def test_user_registration_invalid_password_too_short(self):
        """Test UserRegistration with password too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="newuser", password="short", invite_code="ABC12345"
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("password",)
        assert "at least 8 characters" in errors[0]["msg"]

    def test_user_registration_invalid_password_too_long(self):
        """Test UserRegistration with password too long."""
        long_password = "a" * 129  # 129 characters
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="newuser",
                password=long_password,
                invite_code="ABC12345",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("password",)
        assert "at most 128 characters" in errors[0]["msg"]

    def test_user_registration_invalid_invite_code_too_short(self):
        """Test UserRegistration with invite code too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="newuser",
                password="newpassword123",
                invite_code="SHORT",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("invite_code",)
        assert "at least 8 characters" in errors[0]["msg"]

    def test_user_registration_invalid_invite_code_too_long(self):
        """Test UserRegistration with invite code too long."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="newuser",
                password="newpassword123",
                invite_code="TOOLONGCODE",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("invite_code",)
        assert "at most 8 characters" in errors[0]["msg"]

    def test_user_registration_missing_fields(self):
        """Test UserRegistration with missing required fields."""
        # Missing username
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(password="newpassword123", invite_code="ABC12345")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("username",)
        assert errors[0]["type"] == "missing"

        # Missing password
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(username="newuser", invite_code="ABC12345")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("password",)
        assert errors[0]["type"] == "missing"

        # Missing invite_code
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(username="newuser", password="newpassword123")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("invite_code",)
        assert errors[0]["type"] == "missing"

    def test_user_registration_edge_cases(self):
        """Test UserRegistration with edge case values."""
        # Minimum valid values
        registration = UserRegistration(
            username="abc",  # 3 characters
            password="12345678",  # 8 characters
            invite_code="12345678",  # 8 characters
        )
        assert registration.username == "abc"
        assert registration.password == "12345678"
        assert registration.invite_code == "12345678"

        # Maximum valid values
        long_username = "a" * 50  # 50 characters
        long_password = "a" * 128  # 128 characters
        registration = UserRegistration(
            username=long_username,
            password=long_password,
            invite_code="12345678",
        )
        assert registration.username == long_username
        assert registration.password == long_password
