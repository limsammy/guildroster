# type: ignore[comparison-overlap,assignment,arg-type,attr-defined,return-value]
"""
Integration tests for user authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.token import Token
from app.utils.password import hash_password, verify_password


class TestUserAuthentication:
    def _create_test_superuser(self, db_session: Session) -> tuple[User, str]:
        """Create a test superuser and return user and session_id."""
        # Create superuser
        hashed_password = hash_password("superpassword123")
        user = User(
            username="superuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create session
        from app.models.session import Session as SessionModel

        session = SessionModel.create_session(user_id=user.id)  # type: ignore
        db_session.add(session)
        db_session.commit()

        return user, session.session_id  # type: ignore[return-value]

    def test_create_user_success(self, client: TestClient, db_session: Session):
        """Test successful user creation by superuser."""
        superuser, session_id = self._create_test_superuser(db_session)
        cookies = {"session_id": session_id}

        user_data = {
            "username": "newuser",
            "password": "newpassword123",
            "is_active": True,
            "is_superuser": False,
        }

        response = client.post("/users/", json=user_data, cookies=cookies)
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "password" not in data  # Password should not be returned

    def test_create_user_duplicate_username(
        self, client: TestClient, db_session: Session
    ):
        """Test user creation with duplicate username."""
        superuser, session_id = self._create_test_superuser(db_session)
        cookies = {"session_id": session_id}

        # Create first user
        user_data = {
            "username": "duplicateuser",
            "password": "password123",
            "is_active": True,
            "is_superuser": False,
        }
        response = client.post("/users/", json=user_data, cookies=cookies)
        assert response.status_code == 200

        # Try to create second user with same username
        response = client.post("/users/", json=user_data, cookies=cookies)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_create_user_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test user creation without authentication."""
        user_data = {
            "username": "newuser",
            "password": "newpassword123",
            "is_active": True,
            "is_superuser": False,
        }

        response = client.post("/users/", json=user_data)
        assert response.status_code == 401

    def test_create_user_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test user creation by regular user (not superuser)."""
        # Create regular user
        hashed_password = hash_password("userpassword123")
        user = User(
            username="regularuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        # Create session for regular user
        from app.models.session import Session as SessionModel

        session = SessionModel.create_session(user_id=user.id)  # type: ignore
        db_session.add(session)
        db_session.commit()

        cookies = {"session_id": session.session_id}  # type: ignore[attr-defined]

        user_data = {
            "username": "newuser",
            "password": "newpassword123",
            "is_active": True,
            "is_superuser": False,
        }

        response = client.post("/users/", json=user_data, cookies=cookies)
        assert response.status_code == 403

    def test_login_success(self, client: TestClient, db_session: Session):
        """Test successful user login."""
        # Create user
        hashed_password = hash_password("userpassword123")
        user = User(
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        login_data = {"username": "testuser", "password": "userpassword123"}

        response = client.post("/users/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "user_id" in data
        assert data["username"] == "testuser"
        assert data["user_id"] == user.id
        assert data["is_superuser"] is False

        # Check that session cookie was set
        assert "session_id" in response.cookies

    def test_login_wrong_password(
        self, client: TestClient, db_session: Session
    ):
        """Test login with wrong password."""
        # Create user
        hashed_password = hash_password("userpassword123")
        user = User(
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        login_data = {"username": "testuser", "password": "wrongpassword"}

        response = client.post("/users/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(
        self, client: TestClient, db_session: Session
    ):
        """Test login with non-existent user."""
        login_data = {"username": "nonexistent", "password": "password123"}

        response = client.post("/users/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """Test login with inactive user."""
        # Create inactive user
        hashed_password = hash_password("userpassword123")
        user = User(
            username="inactiveuser",
            hashed_password=hashed_password,
            is_active=False,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        login_data = {"username": "inactiveuser", "password": "userpassword123"}

        response = client.post("/users/login", json=login_data)
        assert response.status_code == 401
        assert "User account is inactive" in response.json()["detail"]

    def test_update_user_success(self, client: TestClient, db_session: Session):
        """Test successful user update by superuser."""
        superuser, session_id = self._create_test_superuser(db_session)
        cookies = {"session_id": session_id}

        # Create user to update
        hashed_password = hash_password("oldpassword123")
        user = User(
            username="updateuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        update_data = {
            "username": "updateduser",
            "password": "newpassword123",
            "is_active": False,
        }

        response = client.put(
            f"/users/{user.id}", json=update_data, cookies=cookies
        )
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "updateduser"
        assert data["is_active"] is False

    def test_delete_user_success(self, client: TestClient, db_session: Session):
        """Test successful user deletion by superuser."""
        superuser, session_id = self._create_test_superuser(db_session)
        cookies = {"session_id": session_id}

        # Create user to delete
        hashed_password = hash_password("userpassword123")
        user = User(
            username="deleteuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        response = client.delete(f"/users/{user.id}", cookies=cookies)
        assert response.status_code == 200
        assert "User deleted successfully" in response.json()["message"]

    def test_delete_user_self_deletion_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that superuser cannot delete their own account."""
        superuser, session_id = self._create_test_superuser(db_session)
        cookies = {"session_id": session_id}

        response = client.delete(f"/users/{superuser.id}", cookies=cookies)
        assert response.status_code == 400
        assert "Cannot delete your own account" in response.json()["detail"]
