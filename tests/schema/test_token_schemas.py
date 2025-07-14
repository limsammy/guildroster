# type: ignore[comparison-overlap,assignment]
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.schemas.token import (
    TokenBase,
    TokenCreate,
    TokenResponse,
    TokenListResponse,
    TokenCreateResponse,
)


class TestTokenBase:
    def test_valid_token_base(self):
        """Test creating a valid TokenBase instance."""
        data = {"token_type": "system", "name": "Test Token", "is_active": True}
        token = TokenBase(**data)
        assert token.token_type == "system"
        assert token.name == "Test Token"
        assert token.is_active is True
        assert token.expires_at is None

    def test_token_base_with_expiration(self):
        """Test TokenBase with expiration date."""
        expires_at = datetime.now() + timedelta(days=7)
        data = {
            "token_type": "user",
            "name": "User Token",
            "expires_at": expires_at,
            "is_active": False,
        }
        token = TokenBase(**data)
        assert token.token_type == "user"
        assert token.expires_at == expires_at
        assert token.is_active is False

    def test_token_base_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            TokenBase(name="Test Token")  # Missing token_type

    def test_token_base_invalid_types(self):
        """Test that invalid types raise validation errors."""
        with pytest.raises(ValidationError):
            TokenBase(
                token_type=123,  # Should be string
                is_active="not_boolean",  # Should be boolean
            )


class TestTokenCreate:
    def test_valid_token_create(self):
        """Test creating a valid TokenCreate instance."""
        data = {
            "token_type": "user",
            "user_id": 1,
            "name": "User Token",
            "is_active": True,
        }
        token = TokenCreate(**data)
        assert token.token_type == "user"
        assert token.user_id == 1
        assert token.name == "User Token"
        assert token.is_active is True

    def test_token_create_system_token(self):
        """Test TokenCreate for system token (no user_id)."""
        data = {"token_type": "system", "name": "System Token"}
        token = TokenCreate(**data)
        assert token.token_type == "system"
        assert token.user_id is None

    def test_token_create_api_token(self):
        """Test TokenCreate for API token."""
        data = {"token_type": "api", "name": "API Token"}
        token = TokenCreate(**data)
        assert token.token_type == "api"
        assert token.user_id is None


class TestTokenResponse:
    def test_valid_token_response(self):
        """Test creating a valid TokenResponse instance."""
        now = datetime.now()
        data = {
            "id": 1,
            "key": "test_key_123",
            "user_id": 1,
            "token_type": "user",
            "name": "User Token",
            "created_at": now,
            "expires_at": None,
            "is_active": True,
        }
        token = TokenResponse(**data)
        assert token.id == 1
        assert token.key == "test_key_123"
        assert token.user_id == 1
        assert token.token_type == "user"
        assert token.name == "User Token"
        assert token.created_at == now

    def test_token_response_system_token(self):
        """Test TokenResponse for system token."""
        now = datetime.now()
        data = {
            "id": 2,
            "key": "system_key_456",
            "user_id": None,
            "token_type": "system",
            "name": "System Token",
            "created_at": now,
            "expires_at": None,
            "is_active": True,
        }
        token = TokenResponse(**data)
        assert token.user_id is None
        assert token.token_type == "system"

    def test_token_response_from_orm(self):
        """Test creating TokenResponse from SQLAlchemy model."""
        from app.models.token import Token

        # Create a mock SQLAlchemy token object
        token_model = Token(
            id=1,
            key="test_key",
            user_id=1,
            token_type="user",
            name="Test Token",
            created_at=datetime.now(),
            is_active=True,
        )

        # Test conversion using model_validate
        token_response = TokenResponse.model_validate(token_model)
        assert token_response.id == 1
        assert token_response.key == "test_key"
        assert token_response.token_type == "user"

    def test_token_response_missing_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            TokenResponse(
                token_type="user",
                name="Test Token",
                # Missing id, key, created_at
            )


class TestTokenListResponse:
    def test_valid_token_list_response(self):
        """Test creating a valid TokenListResponse instance."""
        now = datetime.now()
        tokens = [
            TokenResponse(
                id=1,
                key="key1",
                user_id=1,
                token_type="user",
                name="User Token",
                created_at=now,
                is_active=True,
            ),
            TokenResponse(
                id=2,
                key="key2",
                user_id=None,
                token_type="system",
                name="System Token",
                created_at=now,
                is_active=True,
            ),
        ]

        response = TokenListResponse(tokens=tokens, total=2)
        assert len(response.tokens) == 2
        assert response.total == 2
        assert response.tokens[0].token_type == "user"
        assert response.tokens[1].token_type == "system"

    def test_token_list_response_empty(self):
        """Test creating TokenListResponse with empty token list."""
        response = TokenListResponse(tokens=[], total=0)
        assert len(response.tokens) == 0
        assert response.total == 0

    def test_token_list_response_missing_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            TokenListResponse(tokens=[])  # Missing total


class TestTokenCreateResponse:
    def test_valid_token_create_response(self):
        """Test creating a valid TokenCreateResponse instance."""
        now = datetime.now()
        token = TokenResponse(
            id=1,
            key="new_key",
            user_id=1,
            token_type="user",
            name="New Token",
            created_at=now,
            is_active=True,
        )

        response = TokenCreateResponse(token=token)
        assert response.token == token
        assert response.message == "Token created successfully"

    def test_token_create_response_custom_message(self):
        """Test TokenCreateResponse with custom message."""
        now = datetime.now()
        token = TokenResponse(
            id=1,
            key="new_key",
            user_id=1,
            token_type="user",
            name="New Token",
            created_at=now,
            is_active=True,
        )

        response = TokenCreateResponse(
            token=token, message="Custom success message"
        )
        assert response.token == token
        assert response.message == "Custom success message"
