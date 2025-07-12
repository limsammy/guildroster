import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.token import Token
from app.models.user import User


class TestTokenModel:
    def test_token_creation(self, db_session):
        """Test basic token creation."""
        token = Token(
            key="test_key_123",
            user_id=None,
            token_type="system",
            name="Test Token",
        )

        db_session.add(token)
        db_session.commit()

        assert token.id is not None
        assert token.key == "test_key_123"
        assert token.token_type == "system"
        assert token.name == "Test Token"
        assert token.is_active is True
        assert token.expires_at is None

    def test_token_with_user(self, db_session):
        """Test token creation with user relationship."""
        # Create a user first
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token = Token(
            key="user_key_123",
            user_id=user.id,
            token_type="user",
            name="User Token",
        )

        db_session.add(token)
        db_session.commit()

        assert token.user_id == user.id
        assert token.user == user

    def test_token_unique_key_constraint(self, db_session):
        """Test that token keys must be unique."""
        token1 = Token(key="duplicate_key", token_type="system")
        token2 = Token(key="duplicate_key", token_type="system")

        db_session.add(token1)
        db_session.commit()

        db_session.add(token2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_token_expiration(self, db_session):
        """Test token expiration logic."""
        # Token with no expiration
        token_no_expiry = Token(key="no_expiry", token_type="system")
        assert token_no_expiry.is_expired() is False
        assert token_no_expiry.is_valid() is True

        # Token with future expiration
        future_expiry = datetime.now() + timedelta(days=1)
        token_future = Token(
            key="future_expiry", token_type="system", expires_at=future_expiry
        )
        assert token_future.is_expired() is False
        assert token_future.is_valid() is True

        # Token with past expiration
        past_expiry = datetime.now() - timedelta(days=1)
        token_past = Token(
            key="past_expiry", token_type="system", expires_at=past_expiry
        )
        assert token_past.is_expired() is True
        assert token_past.is_valid() is False

    def test_token_inactive(self, db_session):
        """Test inactive token validation."""
        token = Token(
            key="inactive_token", token_type="system", is_active=False
        )
        assert token.is_valid() is False

    def test_generate_key(self):
        """Test key generation."""
        key1 = Token.generate_key()
        key2 = Token.generate_key()

        assert isinstance(key1, str)
        assert len(key1) > 0
        assert key1 != key2  # Keys should be unique

    def test_create_user_token(self, db_session):
        """Test user token creation."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token = Token.create_user_token(user_id=user.id, name="Test User Token")

        assert token.user_id == user.id
        assert token.token_type == "user"
        assert token.name == "Test User Token"
        assert token.is_active is True
        assert token.expires_at is None

    def test_create_user_token_with_expiration(self, db_session):
        """Test user token creation with expiration."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token = Token.create_user_token(
            user_id=user.id, name="Expiring Token", expires_in_days=7
        )

        assert token.user_id == user.id
        assert token.token_type == "user"
        assert token.expires_at is not None
        assert token.expires_at > datetime.now()

    def test_create_system_token(self, db_session):
        """Test system token creation."""
        token = Token.create_system_token("Frontend App")

        assert token.user_id is None
        assert token.token_type == "system"
        assert token.name == "Frontend App"
        assert token.is_active is True

    def test_create_api_token(self, db_session):
        """Test API token creation."""
        token = Token.create_api_token("Mobile App")

        assert token.user_id is None
        assert token.token_type == "api"
        assert token.name == "Mobile App"
        assert token.is_active is True

    def test_token_database_operations(self, db_session):
        """Test token database operations."""
        # Create and save token
        token = Token.create_system_token("Test Token")
        db_session.add(token)
        db_session.commit()

        # Query token
        queried_token = db_session.query(Token).filter_by(key=token.key).first()
        assert queried_token is not None
        assert queried_token.token_type == "system"
        assert queried_token.name == "Test Token"

    def test_token_user_relationship(self, db_session):
        """Test token-user relationship."""
        # Create user and token
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token = Token.create_user_token(user.id, "User Token")
        db_session.add(token)
        db_session.commit()

        # Test relationship
        assert token.user == user
        assert user.tokens[0] == token

    def test_multiple_tokens_per_user(self, db_session):
        """Test that a user can have multiple tokens."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token1 = Token.create_user_token(user.id, "Token 1")
        token2 = Token.create_user_token(user.id, "Token 2")

        db_session.add_all([token1, token2])
        db_session.commit()

        assert len(user.tokens) == 2
        assert token1 in user.tokens
        assert token2 in user.tokens
