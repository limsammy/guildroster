import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.utils.session_auth import (
    get_session_from_cookie,
    get_current_session,
    get_current_user,
)
from app.utils.auth import require_user, require_superuser
from app.models.session import Session as SessionModel
from app.models.user import User


class TestSessionAuth:
    def setup_user(self) -> User:
        """Create a test user."""
        return User(
            id=1,
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
        )

    def setup_session(self, user: User) -> SessionModel:
        """Create a test session."""
        return SessionModel(
            id=1,
            session_id="test_session_id",
            user_id=user.id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            is_active=True,
        )

    @patch("app.utils.session_auth.get_db")
    def test_get_session_from_cookie_valid_session(self, mock_get_db):
        """Test getting a valid session from cookie."""
        user = self.setup_user()
        session = self.setup_session(user)

        # Mock request and database
        mock_request = Mock()
        mock_request.cookies.get.return_value = "test_session_id"

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = (
            session
        )
        mock_get_db.return_value = mock_db

        result = get_session_from_cookie(mock_request, mock_db)

        assert result == session
        mock_request.cookies.get.assert_called_once_with("session_id")

    @patch("app.utils.session_auth.get_db")
    def test_get_session_from_cookie_no_cookie(self, mock_get_db):
        """Test getting session when no cookie is present."""
        mock_request = Mock()
        mock_request.cookies.get.return_value = None

        mock_db = Mock()
        mock_get_db.return_value = mock_db

        result = get_session_from_cookie(mock_request, mock_db)

        assert result is None
        mock_request.cookies.get.assert_called_once_with("session_id")

    @patch("app.utils.session_auth.get_db")
    def test_get_session_from_cookie_invalid_session(self, mock_get_db):
        """Test getting session when session is not found in database."""
        mock_request = Mock()
        mock_request.cookies.get.return_value = "invalid_session_id"

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = mock_db

        result = get_session_from_cookie(mock_request, mock_db)

        assert result is None

    @patch("app.utils.session_auth.get_db")
    def test_get_session_from_cookie_expired_session(self, mock_get_db):
        """Test getting session when session is expired."""
        user = self.setup_user()
        session = self.setup_session(user)
        session.expires_at = datetime.now() - timedelta(hours=1)  # Expired

        mock_request = Mock()
        mock_request.cookies.get.return_value = "test_session_id"

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = (
            session
        )
        mock_get_db.return_value = mock_db

        result = get_session_from_cookie(mock_request, mock_db)

        assert result is None

    @patch("app.utils.session_auth.get_db")
    def test_get_session_from_cookie_inactive_session(self, mock_get_db):
        """Test getting session when session is inactive."""
        user = self.setup_user()
        session = self.setup_session(user)
        session.is_active = False  # type: ignore

        mock_request = Mock()
        mock_request.cookies.get.return_value = "test_session_id"

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = (
            session
        )
        mock_get_db.return_value = mock_db

        result = get_session_from_cookie(mock_request, mock_db)

        assert result is None

    @patch("app.utils.session_auth.get_session_from_cookie")
    def test_get_current_session_valid(self, mock_get_session):
        """Test getting current session with valid session."""
        user = self.setup_user()
        session = self.setup_session(user)

        mock_request = Mock()
        mock_db = Mock()
        mock_get_session.return_value = session

        result = get_current_session(mock_request, mock_db)

        assert result == session
        mock_get_session.assert_called_once_with(mock_request, mock_db)

    @patch("app.utils.session_auth.get_session_from_cookie")
    def test_get_current_session_invalid(self, mock_get_session):
        """Test getting current session with invalid session."""
        mock_request = Mock()
        mock_db = Mock()
        mock_get_session.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_session(mock_request, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @patch("app.utils.session_auth.get_db")
    def test_get_current_user_valid(self, mock_get_db):
        """Test getting current user with valid session."""
        user = self.setup_user()
        session = self.setup_session(user)

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_get_db.return_value = mock_db

        result = get_current_user(session, mock_db)

        assert result == user
        mock_db.query.assert_called_once()

    @patch("app.utils.session_auth.get_db")
    def test_get_current_user_not_found(self, mock_get_db):
        """Test getting current user when user is not found."""
        session = self.setup_session(self.setup_user())

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = mock_db

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(session, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"

    @patch("app.utils.session_auth.get_db")
    def test_get_current_user_inactive(self, mock_get_db):
        """Test getting current user when user is inactive."""
        user = self.setup_user()
        user.is_active = False  # type: ignore
        session = self.setup_session(user)

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_get_db.return_value = mock_db

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(session, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User is inactive"

    def test_require_user_valid(self):
        """Test require_user with valid user."""
        user = self.setup_user()

        result = require_user(user)

        assert result == user

    def test_require_user_none(self):
        """Test require_user with no user."""
        with pytest.raises(HTTPException) as exc_info:
            require_user(None)  # type: ignore

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Authentication required"

    def test_require_superuser_valid(self):
        """Test require_superuser with valid superuser."""
        user = self.setup_user()
        user.is_superuser = True

        result = require_superuser(user)

        assert result == user

    def test_require_superuser_not_superuser(self):
        """Test require_superuser with non-superuser."""
        user = self.setup_user()
        user.is_superuser = False

        with pytest.raises(HTTPException) as exc_info:
            require_superuser(user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Superuser access required"

    @patch("app.utils.auth.get_current_user")
    def test_require_user_dependency(self, mock_get_current_user):
        """Test require_user as a dependency."""
        user = self.setup_user()
        mock_get_current_user.return_value = user

        result = require_user(user)

        assert result == user

    @patch("app.utils.auth.require_user")
    def test_require_superuser_dependency(self, mock_require_user):
        """Test require_superuser as a dependency."""
        user = self.setup_user()
        user.is_superuser = True
        mock_require_user.return_value = user

        result = require_superuser(user)

        assert result == user
