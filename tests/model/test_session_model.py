import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel
from app.models.user import User


class TestSessionModel:
    def setup_user(self, db_session: Session) -> User:
        """Create a test user for session testing."""
        user = User(
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_create_session(self, db_session: Session):
        """Test creating a new session."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)  # type: ignore
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.id is not None
        assert session.session_id is not None
        assert len(session.session_id) > 20  # type: ignore # Should be a secure random string
        assert session.user_id == user.id
        assert session.is_active is True  # type: ignore
        assert session.created_at is not None
        assert session.expires_at is not None  # type: ignore
        assert session.expires_at > datetime.now()  # type: ignore

    def test_create_session_with_custom_expiration(self, db_session: Session):
        """Test creating a session with custom expiration."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(
            user_id=user.id, expires_in_days=1
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        # Check that expiration is approximately 1 day from now
        expected_expiry = datetime.now() + timedelta(days=1)
        time_diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert time_diff < 10  # Within 10 seconds

    def test_session_is_valid(self, db_session: Session):
        """Test session validation when session is active and not expired."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_valid() is True

    def test_session_is_invalid_when_inactive(self, db_session: Session):
        """Test session validation when session is inactive."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        session.is_active = False
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_valid() is False

    def test_session_is_invalid_when_expired(self, db_session: Session):
        """Test session validation when session is expired."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        session.expires_at = datetime.now() - timedelta(
            hours=1
        )  # Expired 1 hour ago
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_valid() is False

    def test_session_is_invalid_when_both_inactive_and_expired(
        self, db_session: Session
    ):
        """Test session validation when session is both inactive and expired."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        session.is_active = False
        session.expires_at = datetime.now() - timedelta(hours=1)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_valid() is False

    def test_session_expiration_check(self, db_session: Session):
        """Test session expiration checking."""
        user = self.setup_user(db_session)

        # Test non-expired session
        session = SessionModel.create_session(user_id=user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_expired() is False

        # Test expired session
        session.expires_at = datetime.now() - timedelta(minutes=1)
        db_session.commit()
        db_session.refresh(session)

        assert session.is_expired() is True

    def test_session_id_uniqueness(self, db_session: Session):
        """Test that session IDs are unique."""
        user = self.setup_user(db_session)

        session1 = SessionModel.create_session(user_id=user.id)
        session2 = SessionModel.create_session(user_id=user.id)

        db_session.add(session1)
        db_session.add(session2)
        db_session.commit()

        assert session1.session_id != session2.session_id

    def test_session_user_relationship(self, db_session: Session):
        """Test the relationship between session and user."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        # Test that we can access the user through the relationship
        assert session.user is not None
        assert session.user.id == user.id
        assert session.user.username == user.username

    def test_user_sessions_relationship(self, db_session: Session):
        """Test the relationship between user and sessions."""
        user = self.setup_user(db_session)

        session1 = SessionModel.create_session(user_id=user.id)
        session2 = SessionModel.create_session(user_id=user.id)

        db_session.add(session1)
        db_session.add(session2)
        db_session.commit()
        db_session.refresh(user)

        # Test that we can access sessions through the user relationship
        assert len(user.sessions) == 2
        session_ids = [s.session_id for s in user.sessions]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

    def test_session_cascade_delete(self, db_session: Session):
        """Test that sessions are deleted when user is deleted."""
        user = self.setup_user(db_session)

        session = SessionModel.create_session(user_id=user.id)
        db_session.add(session)
        db_session.commit()

        # Verify session exists
        assert (
            db_session.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
            is not None
        )

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify session is also deleted
        assert (
            db_session.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
            is None
        )

    def test_generate_session_id(self, db_session: Session):
        """Test session ID generation."""
        session_id1 = SessionModel.generate_session_id()
        session_id2 = SessionModel.generate_session_id()

        # Check that IDs are different and have reasonable length
        assert session_id1 != session_id2
        assert len(session_id1) >= 32
        assert len(session_id2) >= 32

        # Check that IDs are URL-safe
        assert "=" not in session_id1
        assert "=" not in session_id2
        assert "+" not in session_id1
        assert "+" not in session_id2
        assert "/" not in session_id1
        assert "/" not in session_id2
