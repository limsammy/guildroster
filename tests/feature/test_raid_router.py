# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.raid import Raid
from app.models.token import Token
from app.utils.password import hash_password


class TestRaidAPI:
    def _create_superuser(self, db_session: Session):
        """Helper method to create a superuser with token."""
        user = User(
            username="superuser",
            hashed_password=hash_password("superpassword123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id  # Store ID before making API request
        token = Token.create_user_token(user_id, "Superuser Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_regular_user(self, db_session: Session):
        """Helper method to create a regular user with token."""
        user = User(
            username="regularuser",
            hashed_password=hash_password("userpassword123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id  # Store ID before making API request
        token = Token.create_user_token(user_id, "User Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_guild(self, db_session: Session, user_id: int):
        """Helper method to create a guild."""
        guild = Guild(
            name="Test Guild",
            created_by=user_id,
        )
        db_session.add(guild)
        db_session.commit()
        return guild.id  # Store ID before making API request

    def _create_team(self, db_session: Session, guild_id: int, user_id: int):
        """Helper method to create a team."""
        team = Team(
            name="Test Team",
            guild_id=guild_id,
            created_by=user_id,
        )
        db_session.add(team)
        db_session.commit()
        return team.id  # Store ID before making API request

    def test_create_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "difficulty": "Normal",
            "size": "10",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["scheduled_at"] == scheduled_at.isoformat()
        assert resp["difficulty"] == "Normal"
        assert resp["size"] == "10"
        assert resp["team_id"] == team_id
        assert "id" in resp
        assert "created_at" in resp
        assert "updated_at" in resp

    def test_create_raid_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot create raids."""
        user_id, token_key = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "difficulty": "Normal",
            "size": "10",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_raid_invalid_difficulty(
        self, client: TestClient, db_session: Session
    ):
        """Test creating raid with invalid difficulty."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "difficulty": "Invalid",
            "size": "10",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 422
        assert "Invalid difficulty" in response.text

    def test_create_raid_invalid_size(
        self, client: TestClient, db_session: Session
    ):
        """Test creating raid with invalid size."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "difficulty": "Normal",
            "size": "15",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 422
        assert "Invalid size" in response.text

    def test_create_raid_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating raid with non-existent team."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "difficulty": "Normal",
            "size": "10",
            "team_id": 999,  # Non-existent team
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_list_raids(self, client: TestClient, db_session: Session):
        """Test listing all raids."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        # Create raids
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            difficulty="Heroic",
            size="25",
            team_id=team_id,
        )
        db_session.add_all([raid1, raid2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/raids/", headers=headers)
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 2

    def test_list_raids_filter_by_team(
        self, client: TestClient, db_session: Session
    ):
        """Test listing raids filtered by team."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team1_id = self._create_team(db_session, guild_id, user_id)
        team2 = Team(name="Team 2", guild_id=guild_id, created_by=user_id)
        db_session.add(team2)
        db_session.commit()
        team2_id = team2.id  # Store ID before making API request

        # Create raids in different teams
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            difficulty="Normal",
            size="10",
            team_id=team1_id,
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            difficulty="Heroic",
            size="25",
            team_id=team2_id,
        )
        db_session.add_all([raid1, raid2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/raids/?team_id={team1_id}", headers=headers)
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 1
        assert raids[0]["team_id"] == team1_id

    def test_get_raid_by_id(self, client: TestClient, db_session: Session):
        """Test getting a raid by ID."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/raids/{raid_id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == raid_id
        assert resp["scheduled_at"] == scheduled_at.isoformat()
        assert resp["difficulty"] == "Normal"
        assert resp["size"] == "10"
        assert resp["team_id"] == team_id

    def test_get_raid_not_found(self, client: TestClient, db_session: Session):
        """Test getting a non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/raids/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_raids_by_team(self, client: TestClient, db_session: Session):
        """Test getting raids for a specific team."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        # Create raids for the team
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            difficulty="Heroic",
            size="25",
            team_id=team_id,
        )
        db_session.add_all([raid1, raid2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/raids/team/{team_id}", headers=headers)
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 2
        assert all(raid["team_id"] == team_id for raid in raids)

    def test_get_raids_by_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting raids for a non-existent team."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/raids/team/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        new_scheduled_at = datetime.now() + timedelta(days=2)
        data = {
            "scheduled_at": new_scheduled_at.isoformat(),
            "difficulty": "Heroic",
            "size": "25",
        }
        response = client.put(f"/raids/{raid_id}", json=data, headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["scheduled_at"] == new_scheduled_at.isoformat()
        assert resp["difficulty"] == "Heroic"
        assert resp["size"] == "25"
        assert resp["team_id"] == team_id

    def test_update_raid_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot update raids."""
        user_id, token_key = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"difficulty": "Heroic"}
        response = client.put(f"/raids/{raid_id}", json=data, headers=headers)
        assert response.status_code == 403

    def test_update_raid_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"difficulty": "Heroic"}
        response = client.put("/raids/999", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_raid_invalid_difficulty(
        self, client: TestClient, db_session: Session
    ):
        """Test updating raid with invalid difficulty."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"difficulty": "Invalid"}
        response = client.put(f"/raids/{raid_id}", json=data, headers=headers)
        assert response.status_code == 422
        assert "Invalid difficulty" in response.text

    def test_update_raid_invalid_size(
        self, client: TestClient, db_session: Session
    ):
        """Test updating raid with invalid size."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"size": "15"}
        response = client.put(f"/raids/{raid_id}", json=data, headers=headers)
        assert response.status_code == 422
        assert "Invalid size" in response.text

    def test_update_raid_new_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating raid with non-existent team."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"team_id": 999}  # Non-existent team
        response = client.put(f"/raids/{raid_id}", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/raids/{raid_id}", headers=headers)
        assert response.status_code == 204

        # Verify raid was deleted
        get_response = client.get(f"/raids/{raid_id}", headers=headers)
        assert get_response.status_code == 404

    def test_delete_raid_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot delete raids."""
        user_id, token_key = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            difficulty="Normal",
            size="10",
            team_id=team_id,
        )
        db_session.add(raid)
        db_session.commit()
        raid_id = raid.id  # Store ID before making API request

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/raids/{raid_id}", headers=headers)
        assert response.status_code == 403

    def test_delete_raid_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete("/raids/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_raid_endpoints_require_authentication(
        self, client: TestClient, db_session: Session
    ):
        """Test that all raid endpoints require authentication."""
        endpoints = [
            (
                "POST",
                "/raids/",
                {
                    "scheduled_at": "2024-01-01T10:00:00",
                    "difficulty": "Normal",
                    "size": "10",
                    "team_id": 1,
                },
            ),
            ("GET", "/raids/", None),
            ("GET", "/raids/1", None),
            ("GET", "/raids/team/1", None),
            ("PUT", "/raids/1", {"difficulty": "Heroic"}),
            ("DELETE", "/raids/1", None),
        ]

        for method, endpoint, data in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            elif method == "PUT":
                response = client.put(endpoint, json=data)
            elif method == "DELETE":
                response = client.delete(endpoint)

            assert response.status_code == 401
