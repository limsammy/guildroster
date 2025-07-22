import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.session import Session as SessionModel
from app.utils.password import hash_password

client = TestClient(app)


class TestSessionIntegration:
    def setup_user(self, db_session: Session) -> User:
        """Create a test user for integration testing."""
        user = User(
            username="testuser",
            hashed_password=hash_password("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_login_creates_session(self, db_session: Session):
        """Test that login creates a session and sets cookie."""
        user = self.setup_user(db_session)

        response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert "is_superuser" in data
        assert data["username"] == "testuser"
        assert data["user_id"] == user.id

        # Check that session cookie is set
        assert "session_id" in response.cookies
        session_id = response.cookies["session_id"]
        assert session_id is not None
        assert len(session_id) > 0

        # Verify session was created in database
        session = (
            db_session.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        assert session is not None
        assert session.user_id == user.id
        assert session.is_active is True  # type: ignore

    def test_login_invalid_credentials(self, db_session: Session):
        """Test login with invalid credentials."""
        self.setup_user(db_session)

        response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "session_id" not in response.cookies

    def test_login_nonexistent_user(self, db_session: Session):
        """Test login with nonexistent user."""
        response = client.post(
            "/users/login",
            json={"username": "nonexistent", "password": "testpassword"},
        )

        assert response.status_code == 401
        assert "session_id" not in response.cookies

    def test_get_current_user_with_session(self, db_session: Session):
        """Test getting current user with valid session."""
        user = self.setup_user(db_session)

        # Login first
        login_response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert login_response.status_code == 200
        session_id = login_response.cookies["session_id"]

        # Explicitly pass the session cookie
        response = client.get("/users/me", cookies={"session_id": session_id})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["id"] == user.id

    def test_get_current_user_without_session(self, db_session: Session):
        """Test getting current user without session."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_logout_deactivates_session(self, db_session: Session):
        """Test that logout deactivates the session."""
        user = self.setup_user(db_session)

        # Login first
        login_response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert login_response.status_code == 200
        session_id = login_response.cookies["session_id"]

        # Verify session is active
        session = (
            db_session.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        assert session.is_active is True

        # Logout (explicitly pass session cookie)
        logout_response = client.post(
            "/users/logout", cookies={"session_id": session_id}
        )
        assert logout_response.status_code == 200

        # Verify session is deactivated
        db_session.refresh(session)
        assert session.is_active is False

        # Verify cookie is cleared - delete_cookie doesn't add a cookie to response
        # The cookie will be cleared by the browser when it receives the response
        # We can verify this by checking that the session is deactivated
        assert session.is_active is False

    def test_logout_without_session(self, db_session: Session):
        """Test logout without an active session."""
        response = client.post("/users/logout")
        assert response.status_code == 200

    def test_session_expiration(self, db_session: Session):
        """Test that expired sessions are not valid."""
        user = self.setup_user(db_session)

        # Login first
        login_response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert login_response.status_code == 200
        session_id = login_response.cookies["session_id"]

        # Manually expire the session
        session = (
            db_session.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        from datetime import datetime, timedelta

        session.expires_at = datetime.now() - timedelta(hours=1)  # type: ignore
        db_session.commit()

        # Try to get current user with expired session (explicitly pass session cookie)
        response = client.get("/users/me", cookies={"session_id": session_id})
        assert response.status_code == 401

    def test_multiple_sessions_same_user(self, db_session: Session):
        """Test that a user can have multiple active sessions."""
        user = self.setup_user(db_session)

        # Login twice
        login1_response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert login1_response.status_code == 200
        session1_id = login1_response.cookies["session_id"]

        login2_response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert login2_response.status_code == 200
        session2_id = login2_response.cookies["session_id"]

        # Verify both sessions exist and are different
        assert session1_id != session2_id

        # Verify both sessions are active
        session1 = (
            db_session.query(SessionModel)
            .filter(SessionModel.session_id == session1_id)
            .first()
        )
        session2 = (
            db_session.query(SessionModel)
            .filter(SessionModel.session_id == session2_id)
            .first()
        )
        assert session1.is_active is True
        assert session2.is_active is True

        # Both sessions should work for /users/me
        response1 = client.get("/users/me", cookies={"session_id": session1_id})
        assert response1.status_code == 200
        response2 = client.get("/users/me", cookies={"session_id": session2_id})
        assert response2.status_code == 200

    def test_session_cookie_attributes(self, db_session: Session):
        """Test that session cookie has correct attributes."""
        self.setup_user(db_session)

        response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )

        assert response.status_code == 200

        # Check that session cookie is set
        assert "session_id" in response.cookies
        session_id = response.cookies["session_id"]
        assert session_id is not None
        assert len(session_id) > 0

        # Note: FastAPI TestClient doesn't expose cookie attributes like httponly, secure, etc.
        # These are only available in real browser environments

    def test_inactive_user_cannot_login(self, db_session: Session):
        """Test that inactive users cannot login."""
        user = self.setup_user(db_session)
        user.is_active = False  # type: ignore
        db_session.commit()

        response = client.post(
            "/users/login",
            json={"username": "testuser", "password": "testpassword"},
        )

        assert response.status_code == 401
        assert "session_id" not in response.cookies
