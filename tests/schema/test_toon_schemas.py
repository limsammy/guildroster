import pytest
from datetime import datetime
from app.schemas.toon import (
    ToonBase,
    ToonCreate,
    ToonUpdate,
    ToonResponse,
    WOW_CLASSES,
    WOW_ROLES,
)


class TestToonSchemas:
    def test_toon_base_valid(self):
        data = {
            "username": "MyToon",
            "class": "Mage",
            "role": "DPS",
            "is_main": True,
        }
        toon = ToonBase(**data)
        assert toon.username == "MyToon"
        assert toon.class_ == "Mage"
        assert toon.role == "DPS"
        assert toon.is_main is True

    @pytest.mark.parametrize("bad_class", ["", "Invalid", "mage", "Palad1n"])
    def test_toon_base_invalid_class(self, bad_class):
        data = {"username": "Toon", "class": bad_class, "role": "DPS"}
        with pytest.raises(ValueError):
            ToonBase(**data)

    @pytest.mark.parametrize("bad_role", ["", "invalid", "dps", "Tanky"])
    def test_toon_base_invalid_role(self, bad_role):
        data = {"username": "Toon", "class": "Mage", "role": bad_role}
        with pytest.raises(ValueError):
            ToonBase(**data)

    def test_toon_create(self):
        data = {
            "username": "MyToon",
            "class": "Priest",
            "role": "Healer",
            "is_main": False,
            "member_id": 123,
        }
        toon = ToonCreate(**data)
        assert toon.member_id == 123
        assert toon.class_ == "Priest"

    def test_toon_update_partial(self):
        data = {"class": "Druid", "is_main": True}
        toon = ToonUpdate(**data)
        assert toon.class_ == "Druid"
        assert toon.username is None
        assert toon.role is None
        assert toon.is_main is True

    def test_toon_update_invalid(self):
        # Provide all required fields, only set the invalid one to a bad value
        with pytest.raises(ValueError):
            ToonUpdate(
                username="Toon",
                role="DPS",
                is_main=False,
                **{"class": "NotAClass"}
            )
        with pytest.raises(ValueError):
            ToonUpdate(
                username="Toon",
                role="NotARole",
                is_main=False,
                **{"class": "Mage"}
            )

    def test_toon_response_serialization(self):
        now = datetime.utcnow()
        data = {
            "id": 1,
            "username": "MyToon",
            "class": "Warrior",
            "role": "Tank",
            "is_main": True,
            "member_id": 42,
            "created_at": now,
            "updated_at": now,
        }
        toon = ToonResponse(**data)
        assert toon.id == 1
        assert toon.class_ == "Warrior"
        assert toon.role == "Tank"
        assert toon.member_id == 42
        assert toon.created_at == now
        assert toon.updated_at == now

    def test_toon_response_alias(self):
        # Accepts both class_ and class as input
        now = datetime.utcnow()
        data = {
            "id": 2,
            "username": "AliasToon",
            "class": "Druid",
            "role": "Healer",
            "is_main": False,
            "member_id": 99,
            "created_at": now,
            "updated_at": now,
        }
        toon = ToonResponse(**data)
        assert toon.class_ == "Druid"
        # Output uses alias
        out = toon.model_dump(by_alias=True)
        assert out["class"] == "Druid"
