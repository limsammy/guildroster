# type: ignore[comparison-overlap,assignment]
import pytest
from datetime import datetime
from app.schemas.guild import GuildBase, GuildCreate, GuildUpdate, GuildResponse
import pydantic


class TestGuildSchemas:
    def test_guild_base_validation(self):
        # Valid
        base = GuildBase(name="My Guild")
        assert base.name == "My Guild"

        # Too short
        with pytest.raises(ValueError):
            GuildBase(name="A")

        # Too long
        with pytest.raises(ValueError):
            GuildBase(name="A" * 51)

    def test_guild_create(self):
        obj = GuildCreate(name="GuildName")
        assert obj.name == "GuildName"

        # name required
        with pytest.raises(pydantic.ValidationError):
            GuildCreate()

    def test_guild_update(self):
        # All optional
        update = GuildUpdate()
        assert update.name is None
        # Valid update
        update2 = GuildUpdate(name="NewName")
        assert update2.name == "NewName"

    def test_guild_response_from_orm(self):
        # Simulate ORM object
        class Dummy:
            def __init__(self, id, name, created_by, created_at, updated_at):
                self.id = id
                self.name = name
                self.created_by = created_by
                self.created_at = created_at
                self.updated_at = updated_at

        now = datetime.now()
        dummy = Dummy(1, "GuildX", 2, now, now)
        resp = GuildResponse.model_validate(dummy)
        assert resp.id == 1
        assert resp.name == "GuildX"
        assert resp.created_by == 2
        assert resp.created_at == now
        assert resp.updated_at == now
