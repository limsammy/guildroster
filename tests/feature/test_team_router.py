import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.token import Token
from app.utils.password import hash_password


class TestTeamAPI:
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
        token = Token.create_user_token(user.id, "Superuser Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user, token.key

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
        token = Token.create_user_token(user.id, "User Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user, token.key

    def _create_guild(self, db_session: Session, user_id: int):
        """Helper method to create a guild."""
        guild = Guild(
            name="Test Guild",
            created_by=user_id,
        )
        db_session.add(guild)
        db_session.commit()
        return guild

    def test_create_team_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating a team as superuser."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Raid Team A",
            "description": "Main raid team",
            "guild_id": guild.id,
            "created_by": superuser.id,
        }
        response = client.post("/teams/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["name"] == "Raid Team A"
        assert resp["description"] == "Main raid team"
        assert resp["guild_id"] == guild.id
        assert resp["created_by"] == superuser.id
        assert resp["is_active"] is True

    def test_create_team_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot create teams."""
        regular_user, token_key = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, regular_user.id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Raid Team A",
            "description": "Main raid team",
            "guild_id": guild.id,
            "created_by": regular_user.id,
        }
        response = client.post("/teams/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_team_duplicate_name_in_guild(
        self, client: TestClient, db_session: Session
    ):
        """Test that team names must be unique within a guild."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Raid Team",
            "guild_id": guild.id,
            "created_by": superuser.id,
        }

        # Create first team
        response1 = client.post("/teams/", json=data, headers=headers)
        assert response1.status_code == 201

        # Try to create second team with same name
        response2 = client.post("/teams/", json=data, headers=headers)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_create_team_same_name_different_guilds(
        self, client: TestClient, db_session: Session
    ):
        """Test that team names can be the same across different guilds."""
        superuser, token_key = self._create_superuser(db_session)
        guild1 = self._create_guild(db_session, superuser.id)
        guild2 = Guild(name="Guild 2", created_by=superuser.id)
        db_session.add(guild2)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Raid Team",
            "guild_id": guild1.id,
            "created_by": superuser.id,
        }

        # Create team in first guild
        response1 = client.post("/teams/", json=data, headers=headers)
        assert response1.status_code == 201

        # Create team with same name in second guild
        data["guild_id"] = guild2.id
        response2 = client.post("/teams/", json=data, headers=headers)
        assert response2.status_code == 201

    def test_create_team_guild_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating team with non-existent guild."""
        superuser, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Raid Team",
            "guild_id": 999,  # Non-existent guild
            "created_by": superuser.id,
        }
        response = client.post("/teams/", json=data, headers=headers)
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_list_teams(self, client: TestClient, db_session: Session):
        """Test listing all teams."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Create teams
        team1 = Team(
            name="Raid Team A",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        team2 = Team(
            name="PvP Team",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add_all([team1, team2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/teams/", headers=headers)
        assert response.status_code == 200
        teams = response.json()
        assert len(teams) == 2

    def test_list_teams_filter_by_guild(
        self, client: TestClient, db_session: Session
    ):
        """Test listing teams filtered by guild."""
        superuser, token_key = self._create_superuser(db_session)
        guild1 = self._create_guild(db_session, superuser.id)
        guild2 = Guild(name="Guild 2", created_by=superuser.id)
        db_session.add(guild2)
        db_session.commit()

        # Create teams in different guilds
        team1 = Team(name="Team A", guild_id=guild1.id, created_by=superuser.id)
        team2 = Team(name="Team B", guild_id=guild1.id, created_by=superuser.id)
        team3 = Team(name="Team C", guild_id=guild2.id, created_by=superuser.id)
        db_session.add_all([team1, team2, team3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/teams/?guild_id={guild1.id}", headers=headers)
        assert response.status_code == 200
        teams = response.json()
        assert len(teams) == 2
        assert all(team["guild_id"] == guild1.id for team in teams)

    def test_get_team_by_id(self, client: TestClient, db_session: Session):
        """Test getting a specific team by ID."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        team = Team(
            name="Raid Team A",
            description="Main raid team",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add(team)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["name"] == "Raid Team A"
        assert resp["description"] == "Main raid team"
        assert resp["guild_id"] == guild.id

    def test_get_team_not_found(self, client: TestClient, db_session: Session):
        """Test getting a non-existent team."""
        superuser, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/teams/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_teams_by_guild(self, client: TestClient, db_session: Session):
        """Test getting all teams for a specific guild."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Create teams
        team1 = Team(name="Team A", guild_id=guild.id, created_by=superuser.id)
        team2 = Team(name="Team B", guild_id=guild.id, created_by=superuser.id)
        db_session.add_all([team1, team2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/teams/guild/{guild.id}", headers=headers)
        assert response.status_code == 200
        teams = response.json()
        assert len(teams) == 2
        assert all(team["guild_id"] == guild.id for team in teams)

    def test_get_teams_by_guild_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting teams for a non-existent guild."""
        superuser, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/teams/guild/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_team_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a team as superuser."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        team = Team(
            name="Original Name",
            description="Original description",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add(team)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Updated Name",
            "description": "Updated description",
            "is_active": False,
        }
        response = client.put(f"/teams/{team.id}", json=data, headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["name"] == "Updated Name"
        assert resp["description"] == "Updated description"
        assert resp["is_active"] is False

    def test_update_team_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot update teams."""
        superuser, _ = self._create_superuser(db_session)
        regular_user, token_key = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, superuser.id)

        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add(team)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"name": "Updated Name"}
        response = client.put(f"/teams/{team.id}", json=data, headers=headers)
        assert response.status_code == 403

    def test_update_team_duplicate_name_in_guild(
        self, client: TestClient, db_session: Session
    ):
        """Test that team names must remain unique within a guild when updating."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Create two teams
        team1 = Team(name="Team A", guild_id=guild.id, created_by=superuser.id)
        team2 = Team(name="Team B", guild_id=guild.id, created_by=superuser.id)
        db_session.add_all([team1, team2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"name": "Team A"}  # Try to rename team2 to team1's name
        response = client.put(f"/teams/{team2.id}", json=data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_delete_team_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a team as superuser."""
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        team = Team(
            name="Team to Delete",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add(team)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 204

        # Verify team is deleted
        get_response = client.get(f"/teams/{team.id}", headers=headers)
        assert get_response.status_code == 404

    def test_delete_team_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot delete teams."""
        superuser, _ = self._create_superuser(db_session)
        regular_user, token_key = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, superuser.id)

        team = Team(
            name="Team to Delete",
            guild_id=guild.id,
            created_by=superuser.id,
        )
        db_session.add(team)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 403

    def test_delete_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a non-existent team."""
        superuser, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete("/teams/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_team_endpoints_require_authentication(
        self, client: TestClient, db_session: Session
    ):
        """Test that all team endpoints require authentication."""
        # Test without authentication
        response = client.get("/teams/")
        assert response.status_code == 401

        response = client.post("/teams/", json={})
        assert response.status_code == 401

        response = client.get("/teams/1")
        assert response.status_code == 401

        response = client.put("/teams/1", json={})
        assert response.status_code == 401

        response = client.delete("/teams/1")
        assert response.status_code == 401
