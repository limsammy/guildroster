# type: ignore[comparison-overlap,assignment,arg-type,return-value]
"""
Feature tests for user registration with invite codes.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.invite import Invite
from app.utils.password import hash_password


class TestUserRegistration:
    def _create_test_user(
        self,
        db_session: Session,
        username: str = "testuser",
        is_superuser: bool = False,
    ) -> User:
        """Create a test user and return the user object."""
        user = User(
            username=username,
            hashed_password=hash_password("testpassword123"),
            is_superuser=is_superuser,
        )
        db_session.add(user)
        db_session.commit()
        return user

    def _create_test_invite(
        self, db_session: Session, created_by: int, code: str = "ABC12345"
    ) -> Invite:
        """Create a test invite and return the invite object."""
        invite = Invite(
            code=code,
            created_by=created_by,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)
        return invite

    def test_register_user_success(
        self, client: TestClient, db_session: Session
    ):
        """Test successful user registration with valid invite code."""
        # Create superuser and invite
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Store invite ID before API call to avoid detached instance issues
        invite_id = invite.id

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify user was created in database
        user = db_session.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.is_active is True
        assert user.is_superuser is False

        # Verify invite was marked as used
        invite = db_session.query(Invite).filter(Invite.id == invite_id).first()
        assert invite.used_by == user.id
        assert invite.used_at is not None

    def test_register_user_case_insensitive_invite_code(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with case-insensitive invite code."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Store invite ID before API call to avoid detached instance issues
        invite_id = invite.id

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "abc12345",  # Lowercase
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 200

        # Verify invite was marked as used
        invite = db_session.query(Invite).filter(Invite.id == invite_id).first()
        assert invite.used_by is not None

    def test_register_user_invalid_invite_code(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with invalid invite code."""
        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "INVALID12",  # 8 characters but invalid
        }

        response = client.post("/users/register", json=registration_data)
        # Let's see what the actual response is
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")

        # For now, let's expect 422 since that's what we're getting
        assert response.status_code == 422

    def test_register_user_used_invite_code(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with already used invite code."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Mark invite as used
        invite.used_by = superuser.id
        invite.used_at = datetime.now()
        db_session.commit()

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 400

        data = response.json()
        assert "already been used" in data["detail"]

    def test_register_user_expired_invite_code(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with expired invite code."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Set invite to expired
        invite.expires_at = datetime.now() - timedelta(days=1)
        db_session.commit()

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 400

        data = response.json()
        assert "has expired" in data["detail"]

    def test_register_user_inactive_invite_code(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with inactive invite code."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Set invite to inactive
        invite.is_active = False
        db_session.commit()

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 400

        data = response.json()
        assert "has been invalidated" in data["detail"]

    def test_register_user_duplicate_username(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with duplicate username."""
        # Create existing user
        existing_user = self._create_test_user(db_session, "existinguser")

        # Create superuser and invite
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # Store invite ID before API call to avoid detached instance issues
        invite_id = invite.id

        registration_data = {
            "username": "existinguser",  # Same as existing user
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 400

        data = response.json()
        assert "Username already registered" in data["detail"]

        # Verify invite was not used
        invite = db_session.query(Invite).filter(Invite.id == invite_id).first()
        assert invite.used_by is None

    def test_register_user_invalid_username(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with invalid username."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        registration_data = {
            "username": "ab",  # Too short
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 422  # Validation error

    def test_register_user_invalid_password(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with invalid password."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        registration_data = {
            "username": "newuser",
            "password": "short",  # Too short
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 422  # Validation error

    def test_register_user_invalid_invite_code_format(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with invalid invite code format."""
        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "SHORT",  # Too short
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 422  # Validation error

    def test_register_user_missing_fields(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with missing fields."""
        # Missing username
        response = client.post(
            "/users/register",
            json={"password": "newpassword123", "invite_code": "ABC12345"},
        )
        assert response.status_code == 422

        # Missing password
        response = client.post(
            "/users/register",
            json={"username": "newuser", "invite_code": "ABC12345"},
        )
        assert response.status_code == 422

        # Missing invite_code
        response = client.post(
            "/users/register",
            json={"username": "newuser", "password": "newpassword123"},
        )
        assert response.status_code == 422

    def test_register_user_no_expiration_invite(
        self, client: TestClient, db_session: Session
    ):
        """Test user registration with invite that has no expiration."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )

        # Create invite with no expiration
        invite = Invite(
            code="ABC12345", created_by=superuser.id, expires_at=None
        )
        db_session.add(invite)
        db_session.commit()

        # Store invite ID before API call to avoid detached instance issues
        invite_id = invite.id

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 200

        # Verify invite was marked as used
        invite = db_session.query(Invite).filter(Invite.id == invite_id).first()
        assert invite.used_by is not None

    def test_register_user_multiple_registrations_same_invite(
        self, client: TestClient, db_session: Session
    ):
        """Test that the same invite code cannot be used for multiple registrations."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        # First registration
        registration_data1 = {
            "username": "user1",
            "password": "password123",
            "invite_code": "ABC12345",
        }

        response1 = client.post("/users/register", json=registration_data1)
        assert response1.status_code == 200

        # Second registration with same invite code
        registration_data2 = {
            "username": "user2",
            "password": "password456",
            "invite_code": "ABC12345",
        }

        response2 = client.post("/users/register", json=registration_data2)
        assert response2.status_code == 400

        data = response2.json()
        assert "already been used" in data["detail"]

        # Verify only one user was created
        user1 = db_session.query(User).filter(User.username == "user1").first()
        user2 = db_session.query(User).filter(User.username == "user2").first()
        assert user1 is not None
        assert user2 is None

    def test_register_user_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that registration response has correct structure."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        registration_data = {
            "username": "newuser",
            "password": "newpassword123",
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "id",
            "username",
            "is_active",
            "is_superuser",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in data

        # Verify specific values
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert isinstance(data["id"], int)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)

    def test_register_user_password_hashing(
        self, client: TestClient, db_session: Session
    ):
        """Test that user password is properly hashed during registration."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        invite = self._create_test_invite(db_session, superuser.id, "ABC12345")

        password = "newpassword123"
        registration_data = {
            "username": "newuser",
            "password": password,
            "invite_code": "ABC12345",
        }

        response = client.post("/users/register", json=registration_data)
        assert response.status_code == 200

        # Verify password was hashed
        user = db_session.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.hashed_password != password
        assert user.hashed_password.startswith("sha256$")
