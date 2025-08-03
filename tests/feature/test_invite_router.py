# type: ignore[comparison-overlap,assignment,arg-type,return-value]
"""
Feature tests for the invite router.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.token import Token
from app.models.invite import Invite
from app.utils.password import hash_password


class TestInviteRouter:
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

    def _create_test_token(self, db_session: Session, user: User = None) -> str:
        """Create a test token and return its key."""
        if user is None:
            token = Token.create_system_token("Test Token")
        else:
            token = Token.create_user_token(user.id, "Test Token")

        db_session.add(token)
        db_session.commit()
        return token.key  # type: ignore[return-value]

    def test_create_invite_superuser_success(
        self, client: TestClient, db_session: Session
    ):
        """Test successful invite creation by superuser."""
        # Create superuser
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        token_key = self._create_test_token(db_session, superuser)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.post(
            "/invites/", headers=headers, json={"expires_in_days": 7}
        )
        assert response.status_code == 200

        data = response.json()
        assert "code" in data
        assert len(data["code"]) == 8
        assert data["code"].isalnum()
        assert data["code"].isupper()
        assert data["created_by"] == superuser.id
        assert data["is_active"] is True
        assert data["used_by"] is None
        assert data["used_at"] is None
        assert data["creator_username"] == "superuser"
        assert data["is_expired"] is False

    def test_create_invite_non_superuser_failure(
        self, client: TestClient, db_session: Session
    ):
        """Test that non-superusers cannot create invites."""
        # Create regular user
        user = self._create_test_user(
            db_session, "regularuser", is_superuser=False
        )
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.post(
            "/invites/", headers=headers, json={"expires_in_days": 7}
        )
        assert response.status_code == 403

    def test_create_invite_no_expiration(
        self, client: TestClient, db_session: Session
    ):
        """Test invite creation with no expiration."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        token_key = self._create_test_token(db_session, superuser)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.post(
            "/invites/", headers=headers, json={"expires_in_days": None}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["expires_at"] is None
        assert data["is_expired"] is False

    def test_create_invite_default_expiration(
        self, client: TestClient, db_session: Session
    ):
        """Test invite creation with default expiration (7 days)."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        token_key = self._create_test_token(db_session, superuser)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.post("/invites/", headers=headers, json={})
        assert response.status_code == 200

        data = response.json()
        assert data["expires_at"] is not None
        assert data["is_expired"] is False

    def test_get_invites_empty(self, client: TestClient, db_session: Session):
        """Test getting invites when user has none."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/invites/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["invites"] == []
        assert data["total"] == 0
        assert data["unused_count"] == 0
        assert data["used_count"] == 0
        assert data["expired_count"] == 0

    def test_get_invites_with_data(
        self, client: TestClient, db_session: Session
    ):
        """Test getting invites with data."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create some invites
        invite1 = Invite(
            code="ABC12345",
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        invite2 = Invite(
            code="DEF67890",
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add_all([invite1, invite2])
        db_session.commit()
        db_session.refresh(invite1)
        db_session.refresh(invite2)

        response = client.get("/invites/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["invites"]) == 2
        assert data["total"] == 2
        assert data["unused_count"] == 2
        assert data["used_count"] == 0
        assert data["expired_count"] == 0

        # Check invite data
        codes = [invite["code"] for invite in data["invites"]]
        assert "ABC12345" in codes
        assert "DEF67890" in codes

    def test_get_invites_pagination(
        self, client: TestClient, db_session: Session
    ):
        """Test invite pagination."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create 5 invites
        invites = []
        for i in range(5):
            invite = Invite(
                code=f"CODE{i}123",
                created_by=user.id,
                expires_at=datetime.now() + timedelta(days=7),
            )
            invites.append(invite)

        db_session.add_all(invites)
        db_session.commit()
        for invite in invites:
            db_session.refresh(invite)

        # Test limit
        response = client.get("/invites/?limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["invites"]) == 2
        assert data["total"] == 5

        # Test skip
        response = client.get("/invites/?skip=2&limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["invites"]) == 2
        assert data["total"] == 5

    def test_get_invite_by_id_success(
        self, client: TestClient, db_session: Session
    ):
        """Test getting a specific invite by ID."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create invite
        invite = Invite(
            code="ABC12345",
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        response = client.get(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == invite.id
        assert data["code"] == "ABC12345"
        assert data["created_by"] == user.id
        assert data["creator_username"] == "testuser"

    def test_get_invite_by_id_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting non-existent invite by ID."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/invites/999", headers=headers)
        assert response.status_code == 404

    def test_get_invite_by_id_wrong_user(
        self, client: TestClient, db_session: Session
    ):
        """Test getting invite created by different user."""
        user1 = self._create_test_user(db_session, "user1")
        user2 = self._create_test_user(db_session, "user2")
        token_key = self._create_test_token(db_session, user2)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create invite with user1
        invite = Invite(
            code="ABC12345",
            created_by=user1.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        # Try to get it with user2
        response = client.get(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 404

    def test_invalidate_invite_success(
        self, client: TestClient, db_session: Session
    ):
        """Test successful invite invalidation."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create invite
        invite = Invite(
            code="ABC12345",
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        response = client.delete(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Invite code invalidated successfully"

        # Verify invite is now inactive
        invite_id = invite.id  # Store the ID before the API call
        invite = db_session.query(Invite).filter(Invite.id == invite_id).first()
        assert invite.is_active is False

    def test_invalidate_invite_already_used(
        self, client: TestClient, db_session: Session
    ):
        """Test invalidation of already used invite."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create used invite
        invite = Invite(
            code="ABC12345",
            created_by=user.id,
            used_by=user.id,
            used_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        response = client.delete(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 400

        data = response.json()
        assert "Cannot invalidate a used invite code" in data["detail"]

    def test_invalidate_invite_already_inactive(
        self, client: TestClient, db_session: Session
    ):
        """Test invalidation of already inactive invite."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create inactive invite
        invite = Invite(
            code="ABC12345",
            created_by=user.id,
            is_active=False,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        response = client.delete(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 400

        data = response.json()
        assert "already invalidated" in data["detail"]

    def test_invalidate_invite_wrong_user(
        self, client: TestClient, db_session: Session
    ):
        """Test invalidation by wrong user."""
        user1 = self._create_test_user(db_session, "user1")
        user2 = self._create_test_user(db_session, "user2")
        token_key = self._create_test_token(db_session, user2)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create invite with user1
        invite = Invite(
            code="ABC12345",
            created_by=user1.id,
            expires_at=datetime.now() + timedelta(days=7),
        )
        db_session.add(invite)
        db_session.commit()
        db_session.refresh(invite)

        # Try to invalidate with user2
        response = client.delete(f"/invites/{invite.id}", headers=headers)
        assert response.status_code == 404

    def test_get_invites_statistics(
        self, client: TestClient, db_session: Session
    ):
        """Test invite statistics calculation."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        # Create various types of invites
        # Unused invite
        invite1 = Invite(
            code="ABC12345",
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7),
        )

        # Used invite
        invite2 = Invite(
            code="DEF67890",
            created_by=user.id,
            used_by=user.id,
            used_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
        )

        # Expired invite
        invite3 = Invite(
            code="GHI11111",
            created_by=user.id,
            expires_at=datetime.now() - timedelta(days=1),
        )

        db_session.add_all([invite1, invite2, invite3])
        db_session.commit()
        db_session.refresh(invite1)
        db_session.refresh(invite2)
        db_session.refresh(invite3)

        response = client.get("/invites/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 3
        assert data["unused_count"] == 2  # invite1 and invite3
        assert data["used_count"] == 1  # invite2
        assert data["expired_count"] == 1  # invite3

    def test_unauthorized_access(self, client: TestClient, db_session: Session):
        """Test unauthorized access to invite endpoints."""
        # Test without token
        response = client.post("/invites/", json={"expires_in_days": 7})
        assert response.status_code == 401

        response = client.get("/invites/")
        assert response.status_code == 401

        response = client.delete("/invites/1")
        assert response.status_code == 401

    def test_invite_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that invite response has correct structure."""
        superuser = self._create_test_user(
            db_session, "superuser", is_superuser=True
        )
        token_key = self._create_test_token(db_session, superuser)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.post(
            "/invites/", headers=headers, json={"expires_in_days": 7}
        )
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "id",
            "code",
            "created_by",
            "used_by",
            "is_active",
            "expires_at",
            "created_at",
            "used_at",
            "creator_username",
            "used_username",
            "is_expired",
        ]

        for field in required_fields:
            assert field in data

    def test_invite_list_response_structure(
        self, client: TestClient, db_session: Session
    ):
        """Test that invite list response has correct structure."""
        user = self._create_test_user(db_session, "testuser")
        token_key = self._create_test_token(db_session, user)
        headers = {"Authorization": f"Bearer {token_key}"}

        response = client.get("/invites/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "invites",
            "total",
            "unused_count",
            "used_count",
            "expired_count",
        ]

        for field in required_fields:
            assert field in data

        assert isinstance(data["invites"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["unused_count"], int)
        assert isinstance(data["used_count"], int)
        assert isinstance(data["expired_count"], int)
