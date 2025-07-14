# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.token import Token
from app.models.user import User


class TestTokenRouter:
    def test_create_token_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test creating token without authentication."""
        token_data = {"token_type": "system", "name": "Test Token"}

        response = client.post("/tokens/", json=token_data)
        assert response.status_code == 401  # Unauthorized

    def test_create_token_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test creating token with regular user (not superuser)."""
        # Create regular user and token
        user = User(
            username="regularuser", hashed_password="hash", is_superuser=False
        )
        db_session.add(user)
        db_session.commit()

        user_token = Token.create_user_token(user.id, "User Token")
        db_session.add(user_token)
        db_session.commit()

        token_data = {"token_type": "system", "name": "Test Token"}

        headers = {"Authorization": f"Bearer {user_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 403  # Forbidden

    def test_create_system_token_success(
        self, client: TestClient, db_session: Session
    ):
        """Test creating system token with superuser."""
        # Create superuser and token
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        token_data = {"token_type": "system", "name": "Frontend App"}

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["token"]["token_type"] == "system"
        assert data["token"]["name"] == "Frontend App"
        assert data["token"]["user_id"] is None
        assert data["message"] == "Token created successfully"

    def test_create_user_token_success(
        self, client: TestClient, db_session: Session
    ):
        """Test creating user token with superuser."""
        # Create superuser and target user
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        target_user = User(username="targetuser", hashed_password="hash")
        db_session.add_all([superuser, target_user])
        db_session.commit()

        # Store the IDs before making API calls
        superuser_id = superuser.id
        target_user_id = target_user.id

        superuser_token = Token.create_user_token(
            superuser_id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        token_data = {
            "token_type": "user",
            "user_id": target_user_id,
            "name": "Target User Token",
        }

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["token"]["token_type"] == "user"
        assert data["token"]["user_id"] == target_user_id
        assert data["token"]["name"] == "Target User Token"

    def test_create_user_token_missing_user_id(
        self, client: TestClient, db_session: Session
    ):
        """Test creating user token without user_id."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        token_data = {
            "token_type": "user",
            "name": "User Token",
            # Missing user_id
        }

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 400
        assert "user_id is required" in response.json()["detail"]

    def test_create_user_token_invalid_user(
        self, client: TestClient, db_session: Session
    ):
        """Test creating user token with non-existent user."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        token_data = {
            "token_type": "user",
            "user_id": 999,  # Non-existent user
            "name": "User Token",
        }

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_create_token_invalid_type(
        self, client: TestClient, db_session: Session
    ):
        """Test creating token with invalid type."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        token_data = {"token_type": "invalid_type", "name": "Test Token"}

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post("/tokens/", json=token_data, headers=headers)
        assert response.status_code == 400
        assert "Invalid token type" in response.json()["detail"]

    def test_get_tokens_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """Test getting tokens without authentication."""
        response = client.get("/tokens/")
        assert response.status_code == 401

    def test_get_tokens_success(self, client: TestClient, db_session: Session):
        """Test getting tokens with superuser."""
        # Create superuser and tokens
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        system_token = Token.create_system_token("System Token")
        api_token = Token.create_api_token("API Token")

        db_session.add_all([superuser_token, system_token, api_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.get("/tokens/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["tokens"]) == 3
        assert data["total"] == 3

    def test_get_tokens_with_type_filter(
        self, client: TestClient, db_session: Session
    ):
        """Test getting tokens filtered by type."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        system_token = Token.create_system_token("System Token")

        db_session.add_all([superuser_token, system_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.get("/tokens/?token_type=system", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["tokens"]) == 1
        assert data["tokens"][0]["token_type"] == "system"

    def test_get_token_by_id_success(
        self, client: TestClient, db_session: Session
    ):
        """Test getting specific token by ID."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        target_token = Token.create_system_token("Target Token")

        db_session.add_all([superuser_token, target_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.get(f"/tokens/{target_token.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == target_token.id
        assert data["token_type"] == "system"
        assert data["name"] == "Target Token"

    def test_get_token_by_id_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting non-existent token."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.get("/tokens/999", headers=headers)
        assert response.status_code == 404
        assert "Token not found" in response.json()["detail"]

    def test_delete_token_success(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting token."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        target_token = Token.create_system_token("Target Token")

        db_session.add_all([superuser_token, target_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.delete(f"/tokens/{target_token.id}", headers=headers)
        assert response.status_code == 200
        assert "Token deleted successfully" in response.json()["message"]

    def test_deactivate_token_success(
        self, client: TestClient, db_session: Session
    ):
        """Test deactivating token."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        target_token = Token.create_system_token("Target Token")

        db_session.add_all([superuser_token, target_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post(
            f"/tokens/{target_token.id}/deactivate", headers=headers
        )
        assert response.status_code == 200
        assert "Token deactivated successfully" in response.json()["message"]

    def test_activate_token_success(
        self, client: TestClient, db_session: Session
    ):
        """Test activating token."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        target_token = Token.create_system_token("Target Token")
        target_token.is_active = False

        db_session.add_all([superuser_token, target_token])
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.post(
            f"/tokens/{target_token.id}/activate", headers=headers
        )
        assert response.status_code == 200
        assert "Token activated successfully" in response.json()["message"]

    def test_token_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that token response has correct structure."""
        superuser = User(
            username="superuser", hashed_password="hash", is_superuser=True
        )
        db_session.add(superuser)
        db_session.commit()

        superuser_token = Token.create_user_token(
            superuser.id, "Superuser Token"
        )
        db_session.add(superuser_token)
        db_session.commit()

        headers = {"Authorization": f"Bearer {superuser_token.key}"}
        response = client.get(f"/tokens/{superuser_token.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "id",
            "key",
            "user_id",
            "token_type",
            "name",
            "created_at",
            "expires_at",
            "is_active",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check data types
        assert isinstance(data["id"], int)
        assert isinstance(data["key"], str)
        assert isinstance(data["token_type"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["created_at"], str)  # ISO format datetime string
