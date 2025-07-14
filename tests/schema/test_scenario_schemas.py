# type: ignore[arg-type]
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.scenario import (
    ScenarioBase,
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
)


class TestScenarioBase:
    def test_valid_scenario_base(self):
        """Test creating a valid ScenarioBase."""
        data = {
            "name": "Blackrock Foundry",
            "is_active": True,
        }
        scenario = ScenarioBase(**data)
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True

    def test_scenario_base_name_trimming(self):
        """Test that whitespace is trimmed from name."""
        data = {
            "name": "  Blackrock Foundry  ",
            "is_active": True,
        }
        scenario = ScenarioBase(**data)
        assert scenario.name == "Blackrock Foundry"

    def test_scenario_base_empty_name(self):
        """Test that empty name raises validation error."""
        data = {
            "name": "",
            "is_active": True,
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioBase(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)

    def test_scenario_base_whitespace_only_name(self):
        """Test that whitespace-only name raises validation error."""
        data = {
            "name": "   ",
            "is_active": True,
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioBase(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)

    def test_scenario_base_name_too_long(self):
        """Test that name too long raises validation error."""
        data = {
            "name": "a" * 101,  # 101 characters
            "is_active": True,
        }
        with pytest.raises(ValidationError):
            ScenarioBase(**data)

    def test_scenario_base_is_active_default(self):
        """Test that is_active defaults to True."""
        data = {
            "name": "Blackrock Foundry",
        }
        scenario = ScenarioBase(**data)
        assert scenario.is_active is True


class TestScenarioCreate:
    def test_valid_scenario_create(self):
        """Test creating a valid ScenarioCreate."""
        data = {
            "name": "Blackrock Foundry",
            "is_active": True,
        }
        scenario = ScenarioCreate(**data)
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True

    def test_scenario_create_inherits_validation(self):
        """Test that ScenarioCreate inherits validation from ScenarioBase."""
        data = {
            "name": "",  # Invalid empty name
            "is_active": True,
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioCreate(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)


class TestScenarioUpdate:
    def test_valid_scenario_update_all_fields(self):
        """Test updating all fields."""
        data = {
            "name": "Updated Scenario",
            "is_active": False,
        }
        scenario = ScenarioUpdate(**data)
        assert scenario.name == "Updated Scenario"
        assert scenario.is_active is False

    def test_valid_scenario_update_partial(self):
        """Test updating only some fields."""
        data = {
            "name": "Updated Scenario",
        }
        scenario = ScenarioUpdate(**data)
        assert scenario.name == "Updated Scenario"
        assert scenario.is_active is None

    def test_scenario_update_name_trimming(self):
        """Test that whitespace is trimmed from name in updates."""
        data = {
            "name": "  Updated Scenario  ",
        }
        scenario = ScenarioUpdate(**data)
        assert scenario.name == "Updated Scenario"

    def test_scenario_update_empty_name(self):
        """Test that empty name raises validation error."""
        data = {
            "name": "",
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioUpdate(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)

    def test_scenario_update_whitespace_only_name(self):
        """Test that whitespace-only name raises validation error."""
        data = {
            "name": "   ",
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioUpdate(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)

    def test_scenario_update_name_too_long(self):
        """Test that name too long raises validation error."""
        data = {
            "name": "a" * 101,  # 101 characters
        }
        with pytest.raises(ValidationError):
            ScenarioUpdate(**data)

    def test_scenario_update_none_name(self):
        """Test that None name is allowed."""
        data = {
            "name": None,
            "is_active": False,
        }
        scenario = ScenarioUpdate(**data)
        assert scenario.name is None
        assert scenario.is_active is False


class TestScenarioResponse:
    def test_valid_scenario_response(self):
        """Test creating a valid ScenarioResponse."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Blackrock Foundry",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        scenario = ScenarioResponse(**data)
        assert scenario.id == 1
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True
        assert scenario.created_at == now
        assert scenario.updated_at == now

    def test_scenario_response_from_orm(self):
        """Test creating ScenarioResponse from ORM model attributes."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Blackrock Foundry",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        # Simulate ORM model with from_attributes=True
        scenario = ScenarioResponse.model_validate(data)
        assert scenario.id == 1
        assert scenario.name == "Blackrock Foundry"
        assert scenario.is_active is True
        assert scenario.created_at == now
        assert scenario.updated_at == now

    def test_scenario_response_inherits_validation(self):
        """Test that ScenarioResponse inherits validation from ScenarioBase."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "",  # Invalid empty name
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        with pytest.raises(ValidationError) as exc_info:
            ScenarioResponse(**data)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)


class TestScenarioSchemaIntegration:
    def test_scenario_create_to_response_flow(self):
        """Test the flow from create to response schema."""
        # Create scenario
        create_data = {
            "name": "Blackrock Foundry",
            "is_active": True,
        }
        create_scenario = ScenarioCreate(**create_data)
        assert create_scenario.name == "Blackrock Foundry"

        # Simulate response with additional fields
        now = datetime.now()
        response_data = {
            "id": 1,
            "name": create_scenario.name,
            "is_active": create_scenario.is_active,
            "created_at": now,
            "updated_at": now,
        }
        response_scenario = ScenarioResponse(**response_data)
        assert response_scenario.id == 1
        assert response_scenario.name == "Blackrock Foundry"

    def test_scenario_update_flow(self):
        """Test the update schema flow."""
        # Original scenario
        original_data = {
            "name": "Original Scenario",
            "is_active": True,
        }
        original = ScenarioBase(**original_data)

        # Update scenario
        update_data = {
            "name": "Updated Scenario",
            "is_active": False,
        }
        update = ScenarioUpdate(**update_data)
        assert update.name == "Updated Scenario"
        assert update.is_active is False

        # Partial update
        partial_update = ScenarioUpdate(name="Partial Update", is_active=None)
        assert partial_update.name == "Partial Update"
        assert partial_update.is_active is None
