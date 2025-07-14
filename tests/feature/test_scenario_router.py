# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.scenario import Scenario
from app.models.token import Token
from app.utils.password import hash_password


class TestScenarioAPI:
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

    def test_create_scenario_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating a scenario as superuser."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Test Scenario",
            "is_active": True,
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["name"] == "Test Scenario"
        assert resp["is_active"] is True
        assert "id" in resp
        assert "created_at" in resp
        assert "updated_at" in resp

    def test_create_scenario_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot create scenarios."""
        user_id, token_key = self._create_regular_user(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Test Scenario",
            "is_active": True,
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_scenario_empty_name(
        self, client: TestClient, db_session: Session
    ):
        """Test creating scenario with empty name."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "",
            "is_active": True,
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 422

    def test_create_scenario_whitespace_name(
        self, client: TestClient, db_session: Session
    ):
        """Test creating scenario with whitespace-only name."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "   ",
            "is_active": True,
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 422

    def test_create_scenario_name_too_long(
        self, client: TestClient, db_session: Session
    ):
        """Test creating scenario with name too long."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "a" * 101,  # 101 characters, max is 100
            "is_active": True,
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 422

    def test_create_scenario_default_is_active(
        self, client: TestClient, db_session: Session
    ):
        """Test creating scenario with default is_active value."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Test Scenario",
        }
        response = client.post("/scenarios/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["name"] == "Test Scenario"
        assert resp["is_active"] is True  # Default value

    def test_list_scenarios(self, client: TestClient, db_session: Session):
        """Test listing scenarios."""
        user_id, token_key = self._create_superuser(db_session)

        # Create some scenarios
        scenario1 = Scenario(name="Scenario 1", is_active=True)
        scenario2 = Scenario(name="Scenario 2", is_active=False)
        scenario3 = Scenario(name="Scenario 3", is_active=True)
        db_session.add_all([scenario1, scenario2, scenario3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/scenarios/", headers=headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) == 3
        names = [s["name"] for s in scenarios]
        assert "Scenario 1" in names
        assert "Scenario 2" in names
        assert "Scenario 3" in names

    def test_list_scenarios_filter_active(
        self, client: TestClient, db_session: Session
    ):
        """Test listing scenarios filtered by is_active=True."""
        user_id, token_key = self._create_superuser(db_session)

        # Create scenarios with different active states
        scenario1 = Scenario(name="Active Scenario 1", is_active=True)
        scenario2 = Scenario(name="Inactive Scenario", is_active=False)
        scenario3 = Scenario(name="Active Scenario 2", is_active=True)
        db_session.add_all([scenario1, scenario2, scenario3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/scenarios/?is_active=true", headers=headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) == 2
        for scenario in scenarios:
            assert scenario["is_active"] is True

    def test_list_scenarios_filter_inactive(
        self, client: TestClient, db_session: Session
    ):
        """Test listing scenarios filtered by is_active=False."""
        user_id, token_key = self._create_superuser(db_session)

        # Create scenarios with different active states
        scenario1 = Scenario(name="Active Scenario", is_active=True)
        scenario2 = Scenario(name="Inactive Scenario 1", is_active=False)
        scenario3 = Scenario(name="Inactive Scenario 2", is_active=False)
        db_session.add_all([scenario1, scenario2, scenario3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/scenarios/?is_active=false", headers=headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) == 2
        for scenario in scenarios:
            assert scenario["is_active"] is False

    def test_get_scenario_by_id(self, client: TestClient, db_session: Session):
        """Test getting a scenario by ID."""
        user_id, token_key = self._create_superuser(db_session)

        # Create a scenario
        scenario = Scenario(name="Test Scenario", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == scenario_id
        assert resp["name"] == "Test Scenario"
        assert resp["is_active"] is True

    def test_get_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting a non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/scenarios/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_active_scenarios(
        self, client: TestClient, db_session: Session
    ):
        """Test getting all active scenarios."""
        user_id, token_key = self._create_superuser(db_session)

        # Create scenarios with different active states
        scenario1 = Scenario(name="Active Scenario 1", is_active=True)
        scenario2 = Scenario(name="Inactive Scenario", is_active=False)
        scenario3 = Scenario(name="Active Scenario 2", is_active=True)
        db_session.add_all([scenario1, scenario2, scenario3])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/scenarios/active", headers=headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) == 2
        for scenario in scenarios:
            assert scenario["is_active"] is True

    def test_update_scenario_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a scenario as superuser."""
        user_id, token_key = self._create_superuser(db_session)

        # Create a scenario
        scenario = Scenario(name="Original Name", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Updated Name",
            "is_active": False,
        }
        response = client.put(
            f"/scenarios/{scenario_id}", json=data, headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == scenario_id
        assert resp["name"] == "Updated Name"
        assert resp["is_active"] is False

    def test_update_scenario_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot update scenarios."""
        user_id, token_key = self._create_regular_user(db_session)

        # Create a scenario
        scenario = Scenario(name="Original Name", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Updated Name",
            "is_active": False,
        }
        response = client.put(
            f"/scenarios/{scenario_id}", json=data, headers=headers
        )
        assert response.status_code == 403

    def test_update_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating a non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Updated Name",
            "is_active": False,
        }
        response = client.put("/scenarios/999", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_scenario_partial(
        self, client: TestClient, db_session: Session
    ):
        """Test updating only some fields of a scenario."""
        user_id, token_key = self._create_superuser(db_session)

        # Create a scenario
        scenario = Scenario(name="Original Name", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "Updated Name",
        }
        response = client.put(
            f"/scenarios/{scenario_id}", json=data, headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == scenario_id
        assert resp["name"] == "Updated Name"
        assert resp["is_active"] is True  # Should remain unchanged

    def test_update_scenario_invalid_name(
        self, client: TestClient, db_session: Session
    ):
        """Test updating scenario with invalid name."""
        user_id, token_key = self._create_superuser(db_session)

        # Create a scenario
        scenario = Scenario(name="Original Name", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "name": "",  # Empty name
            "is_active": False,
        }
        response = client.put(
            f"/scenarios/{scenario_id}", json=data, headers=headers
        )
        assert response.status_code == 422

    def test_delete_scenario_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a scenario as superuser."""
        user_id, token_key = self._create_superuser(db_session)

        # Create a scenario
        scenario = Scenario(name="Test Scenario", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 204

        # Verify scenario is deleted
        response = client.get(f"/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_scenario_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot delete scenarios."""
        user_id, token_key = self._create_regular_user(db_session)

        # Create a scenario
        scenario = Scenario(name="Test Scenario", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 403

    def test_delete_scenario_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting a non-existent scenario."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete("/scenarios/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_scenario_endpoints_require_authentication(
        self, client: TestClient, db_session: Session
    ):
        """Test that all scenario endpoints require authentication."""
        # Create a scenario for testing
        scenario = Scenario(name="Test Scenario", is_active=True)
        db_session.add(scenario)
        db_session.commit()
        scenario_id = scenario.id

        # Test endpoints without authentication
        endpoints = [
            ("POST", "/scenarios/", {"name": "Test", "is_active": True}),
            ("GET", "/scenarios/", None),
            ("GET", f"/scenarios/{scenario_id}", None),
            ("GET", "/scenarios/active", None),
            ("PUT", f"/scenarios/{scenario_id}", {"name": "Updated"}),
            ("DELETE", f"/scenarios/{scenario_id}", None),
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
            else:
                continue

            assert (
                response.status_code == 401
            ), f"Endpoint {method} {endpoint} should require authentication"
