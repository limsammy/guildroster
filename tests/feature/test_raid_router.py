# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.scenario import Scenario
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
        import uuid

        team = Team(
            name=f"Test Team {uuid.uuid4().hex[:8]}",
            guild_id=guild_id,
            created_by=user_id,
        )
        db_session.add(team)
        db_session.commit()
        return team.id  # Store ID before making API request

    def _create_scenario(self, db_session: Session):
        """Helper method to create a scenario."""
        import uuid

        scenario = Scenario(
            name=f"Test Scenario {uuid.uuid4().hex[:8]}",
            is_active=True,
            mop=False,
        )
        db_session.add(scenario)
        db_session.commit()
        return scenario  # Return the scenario object

    def test_create_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "scenario_name": scenario.name,
            "scenario_difficulty": "Normal",
            "scenario_size": "10",
            "team_id": team_id,
            "warcraftlogs_url": "https://www.warcraftlogs.com/reports/test-api",
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["scheduled_at"] == scheduled_at.isoformat()
        assert resp["scenario_name"] == data["scenario_name"]
        assert resp["scenario_difficulty"] == "Normal"
        assert resp["scenario_size"] == "10"
        assert resp["team_id"] == team_id
        assert resp["warcraftlogs_url"] == data["warcraftlogs_url"]
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
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "scenario_name": scenario.name,
            "scenario_difficulty": "Normal",
            "scenario_size": "10",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_raid_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating raid with non-existent team."""
        user_id, token_key = self._create_superuser(db_session)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "scenario_name": scenario.name,
            "scenario_difficulty": "Normal",
            "scenario_size": "10",
            "team_id": 999,  # Non-existent team
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_raid_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating raid with non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        scheduled_at = datetime.now() + timedelta(days=1)
        data = {
            "scheduled_at": scheduled_at.isoformat(),
            "scenario_name": "Non-existent Scenario",
            "scenario_difficulty": "Normal",
            "scenario_size": "10",
            "team_id": team_id,
        }
        response = client.post("/raids/", json=data, headers=headers)
        assert response.status_code == 400
        assert "Invalid scenario variation" in response.json()["detail"]

    def test_list_raids(self, client: TestClient, db_session: Session):
        """Test listing all raids."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        # Create raids
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
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
        team2_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        # Create raids for different teams
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team1_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team1_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid3 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team2_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add_all([raid1, raid2, raid3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/raids/?team_id={team1_id}", headers=headers)
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 2
        assert all(raid["team_id"] == team1_id for raid in raids)

    def test_list_raids_filter_by_scenario(
        self, client: TestClient, db_session: Session
    ):
        """Test listing raids filtered by scenario."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario1 = self._create_scenario(db_session)
        scenario2 = self._create_scenario(db_session)
        db_session.refresh(scenario1)
        db_session.refresh(scenario2)

        # Create raids for different scenarios
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario1.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            scenario_name=scenario1.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid3 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario2.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add_all([raid1, raid2, raid3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/raids/?scenario_name={scenario1.name}", headers=headers
        )
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 2
        assert all(raid["scenario_name"] == scenario1.name for raid in raids)

    def test_get_raid_by_id(self, client: TestClient, db_session: Session):
        """Test getting a specific raid by ID."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)
        scenario_name = scenario.name  # Store the name before API call

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario_name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/raids/{raid.id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["scheduled_at"] == scheduled_at.isoformat()
        assert resp["scenario_name"] == scenario_name
        assert resp["scenario_difficulty"] == "Normal"
        assert resp["scenario_size"] == "10"
        assert resp["team_id"] == team_id
        assert resp["warcraftlogs_url"] == raid.warcraftlogs_url

    def test_get_raid_not_found(self, client: TestClient, db_session: Session):
        """Test getting a non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/raids/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_raids_by_team(self, client: TestClient, db_session: Session):
        """Test getting all raids for a specific team."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        # Create raids
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
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

    def test_get_raids_by_scenario(
        self, client: TestClient, db_session: Session
    ):
        """Test getting all raids for a specific scenario."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        # Create raids
        scheduled_at1 = datetime.now() + timedelta(days=1)
        scheduled_at2 = datetime.now() + timedelta(days=2)
        raid1 = Raid(
            scheduled_at=scheduled_at1,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        raid2 = Raid(
            scheduled_at=scheduled_at2,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add_all([raid1, raid2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/raids/scenario/{scenario.name}", headers=headers
        )
        assert response.status_code == 200
        raids = response.json()
        assert len(raids) == 2
        assert all(raid["scenario_name"] == scenario.name for raid in raids)

    def test_get_raids_by_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting raids for a non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/raids/scenario/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)
        scenario_name = scenario.name  # Store the name before API call

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario_name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        new_scheduled_at = datetime.now() + timedelta(days=2)
        data = {
            "scheduled_at": new_scheduled_at.isoformat(),
        }
        response = client.put(f"/raids/{raid.id}", json=data, headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["scheduled_at"] == new_scheduled_at.isoformat()
        assert resp["scenario_name"] == scenario_name
        assert resp["scenario_difficulty"] == "Normal"
        assert resp["scenario_size"] == "10"
        assert resp["team_id"] == team_id
        assert resp["warcraftlogs_url"] == raid.warcraftlogs_url

    def test_update_raid_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot update raids."""
        user_id, token_key = self._create_regular_user(db_session)
        superuser_id, _ = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, superuser_id)
        team_id = self._create_team(db_session, guild_id, superuser_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat()
        }
        response = client.put(f"/raids/{raid.id}", json=data, headers=headers)
        assert response.status_code == 403

    def test_update_raid_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat()
        }
        response = client.put("/raids/999", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_raid_new_team_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating raid with non-existent team."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"team_id": 999}  # Non-existent team
        response = client.put(f"/raids/{raid.id}", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_raid_new_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating raid with non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "scenario_name": "Non-existent Scenario",
            "scenario_difficulty": "Normal",
            "scenario_size": "10",
        }
        response = client.put(f"/raids/{raid.id}", json=data, headers=headers)
        assert response.status_code == 400
        assert "Invalid scenario variation" in response.json()["detail"]

    def test_delete_raid_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a raid as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        team_id = self._create_team(db_session, guild_id, user_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/raids/{raid.id}", headers=headers)
        assert response.status_code == 204

        # Verify raid is deleted
        get_response = client.get(f"/raids/{raid.id}", headers=headers)
        assert get_response.status_code == 404

    def test_delete_raid_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot delete raids."""
        user_id, token_key = self._create_regular_user(db_session)
        superuser_id, _ = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, superuser_id)
        team_id = self._create_team(db_session, guild_id, superuser_id)
        scenario = self._create_scenario(db_session)
        db_session.refresh(scenario)

        scheduled_at = datetime.now() + timedelta(days=1)
        raid = Raid(
            scheduled_at=scheduled_at,
            scenario_name=scenario.name,
            scenario_difficulty="Normal",
            scenario_size="10",
            team_id=team_id,
            warcraftlogs_url="https://www.warcraftlogs.com/reports/test-api",
        )
        db_session.add(raid)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/raids/{raid.id}", headers=headers)
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
        # Test without authentication
        response = client.get("/raids/")
        assert response.status_code == 401

        response = client.post("/raids/", json={})
        assert response.status_code == 401

        response = client.get("/raids/1")
        assert response.status_code == 401

        response = client.put("/raids/1", json={})
        assert response.status_code == 401

        response = client.delete("/raids/1")
        assert response.status_code == 401
