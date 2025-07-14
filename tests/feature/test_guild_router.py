# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import Token
from app.utils.password import hash_password


class TestGuildAPI:
    def _create_superuser(self, db_session: Session):
        user = User(
            username="superuser",
            hashed_password=hash_password("superpassword123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        token = Token.create_user_token(user.id, "Superuser Token")
        db_session.add(token)
        db_session.commit()
        return user, token.key

    def _create_regular_user(self, db_session: Session):
        user = User(
            username="regularuser",
            hashed_password=hash_password("userpassword123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        token = Token.create_user_token(user.id, "User Token")
        db_session.add(token)
        db_session.commit()
        return user, token.key

    def test_create_guild_superuser(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"name": "Guild1", "created_by": superuser_id}
        response = client.post("/guilds/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["name"] == "Guild1"
        assert resp["created_by"] == superuser_id

    def test_create_guild_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        user, token_key = self._create_regular_user(db_session)
        user_id = user.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"name": "Guild2", "created_by": user_id}
        response = client.post("/guilds/", json=data, headers=headers)
        assert response.status_code == 403

    def test_list_guilds(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        # Create a guild
        data = {"name": "Guild3", "created_by": superuser_id}
        client.post("/guilds/", json=data, headers=headers)
        # List guilds
        response = client.get("/guilds/", headers=headers)
        assert response.status_code == 200
        guilds = response.json()
        assert any(g["name"] == "Guild3" for g in guilds)

    def test_get_guild_by_id(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        # Create a guild
        data = {"name": "Guild4", "created_by": superuser_id}
        resp = client.post("/guilds/", json=data, headers=headers)
        guild_id = resp.json()["id"]
        # Get by id
        response = client.get(f"/guilds/{guild_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == guild_id

    def test_update_guild(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        # Create a guild
        data = {"name": "Guild5", "created_by": superuser_id}
        resp = client.post("/guilds/", json=data, headers=headers)
        guild_id = resp.json()["id"]
        # Update
        update_data = {"name": "Guild5Updated"}
        response = client.put(
            f"/guilds/{guild_id}", json=update_data, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Guild5Updated"

    def test_delete_guild(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        # Create a guild
        data = {"name": "Guild6", "created_by": superuser_id}
        resp = client.post("/guilds/", json=data, headers=headers)
        guild_id = resp.json()["id"]
        # Delete
        response = client.delete(f"/guilds/{guild_id}", headers=headers)
        assert response.status_code == 204
        # Confirm gone
        response = client.get(f"/guilds/{guild_id}", headers=headers)
        assert response.status_code == 404

    def test_create_guild_duplicate_name(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        superuser_id = superuser.id  # Store ID before object gets detached
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"name": "Guild7", "created_by": superuser_id}
        response1 = client.post("/guilds/", json=data, headers=headers)
        assert response1.status_code == 201
        response2 = client.post("/guilds/", json=data, headers=headers)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
