# type: ignore[comparison-overlap,assignment,arg-type,return-value]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.token import Token


class TestUserRouter:
    def _create_test_token(self, db_session: Session) -> str:
        """Create a test system token and return its key."""
        token = Token.create_system_token("Test Token")
        db_session.add(token)
        db_session.commit()
        return token.key  # type: ignore[return-value]

    def test_get_users_empty_database(
        self, client: TestClient, db_session: Session
    ):
        """Test getting users when database is empty."""
        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["users"] == []
        assert data["total"] == 0

    def test_get_users_with_data(self, client: TestClient, db_session: Session):
        """Test getting users with data in database."""
        # Create test users
        user1 = User(username="user1", hashed_password="hash1")
        user2 = User(username="user2", hashed_password="hash2")
        user3 = User(username="user3", hashed_password="hash3")

        db_session.add_all([user1, user2, user3])
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["users"]) == 3
        assert data["total"] == 3

        # Check user data
        usernames = [user["username"] for user in data["users"]]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames

    def test_get_users_pagination(
        self, client: TestClient, db_session: Session
    ):
        """Test user pagination."""
        # Create 5 test users
        users = []
        for i in range(5):
            user = User(username=f"user{i}", hashed_password=f"hash{i}")
            users.append(user)

        db_session.add_all(users)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Test limit
        response = client.get("/users/?limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["users"]) == 2
        assert data["total"] == 5

        # Test skip
        response = client.get("/users/?skip=2&limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["users"]) == 2
        assert data["total"] == 5

    def test_get_user_by_id_success(
        self, client: TestClient, db_session: Session
    ):
        """Test getting user by ID successfully."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get(f"/users/{user.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == "testuser"
        assert data["is_active"] is True
        assert data["is_superuser"] is False

    def test_get_user_by_id_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting user by non-existent ID."""
        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/999", headers=headers)
        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "User not found"

    def test_get_user_by_id_invalid_id(
        self, client: TestClient, db_session: Session
    ):
        """Test getting user with invalid ID format."""
        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/invalid", headers=headers)
        assert response.status_code == 422  # Validation error

    def test_get_user_by_username_success(
        self, client: TestClient, db_session: Session
    ):
        """Test getting user by username successfully."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/username/testuser", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == "testuser"

    def test_get_user_by_username_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting user by non-existent username."""
        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/username/nonexistent", headers=headers)
        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "User not found"

    def test_get_user_by_username_case_sensitive(
        self, client: TestClient, db_session: Session
    ):
        """Test that username lookup is case sensitive."""
        user = User(username="TestUser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Try with different case
        response = client.get("/users/username/testuser", headers=headers)
        assert response.status_code == 404

    def test_user_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that user response has correct structure."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get(f"/users/{user.id}", headers=headers)
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
            assert field in data, f"Missing field: {field}"

        # Check data types
        assert isinstance(data["id"], int)
        assert isinstance(data["username"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["is_superuser"], bool)
        assert isinstance(data["created_at"], str)  # ISO format datetime string
        assert isinstance(data["updated_at"], str)  # ISO format datetime string

    def test_users_list_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that users list response has correct structure."""
        user = User(username="testuser", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        assert isinstance(data["total"], int)

        if data["users"]:
            user_data = data["users"][0]
            required_fields = [
                "id",
                "username",
                "is_active",
                "is_superuser",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                assert field in user_data, f"Missing field: {field}"

    def test_multiple_users_different_states(
        self, client: TestClient, db_session: Session
    ):
        """Test getting users with different active/superuser states."""
        # Create users with different states
        user1 = User(
            username="active_user",
            hashed_password="hash",
            is_active=True,
            is_superuser=False,
        )
        user2 = User(
            username="inactive_user",
            hashed_password="hash",
            is_active=False,
            is_superuser=False,
        )
        user3 = User(
            username="superuser",
            hashed_password="hash",
            is_active=True,
            is_superuser=True,
        )

        db_session.add_all([user1, user2, user3])
        db_session.commit()

        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["users"]) == 3

        # Find users by username and check their states
        users_by_name = {user["username"]: user for user in data["users"]}

        assert users_by_name["active_user"]["is_active"] is True
        assert users_by_name["active_user"]["is_superuser"] is False

        assert users_by_name["inactive_user"]["is_active"] is False
        assert users_by_name["inactive_user"]["is_superuser"] is False

        assert users_by_name["superuser"]["is_active"] is True
        assert users_by_name["superuser"]["is_superuser"] is True

    def test_get_users_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test that getting users without authentication returns 401."""
        response = client.get("/users/")
        assert response.status_code == 401

    def test_get_user_by_id_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test that getting user by ID without authentication returns 401."""
        response = client.get("/users/1")
        assert response.status_code == 401

    def test_get_user_by_username_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test that getting user by username without authentication returns 401."""
        response = client.get("/users/username/testuser")
        assert response.status_code == 401

    def test_health_check_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test that health check without authentication returns 200 (public endpoint)."""
        response = client.get("/")
        assert response.status_code == 200

    def test_health_check_authorized(
        self, client: TestClient, db_session: Session
    ):
        """Test that health check with authentication returns 200."""
        token_key = self._create_test_token(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "GuildRoster API is running" in data["message"]
