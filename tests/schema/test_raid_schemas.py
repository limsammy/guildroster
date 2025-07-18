import pytest
from datetime import datetime, timedelta
from app.schemas.raid import (
    RaidBase,
    RaidCreate,
    RaidUpdate,
    RaidResponse,
)


class TestRaidSchemas:
    def test_raid_base_valid(self):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "scenario_id": 1,
            "team_id": 1,
            "warcraftlogs_url": "https://www.warcraftlogs.com/reports/test",
        }
        raid = RaidBase(**data)
        assert raid.scheduled_at == data["scheduled_at"]
        assert raid.scenario_id == 1
        assert raid.team_id == 1
        assert raid.warcraftlogs_url == data["warcraftlogs_url"]

    def test_raid_create(self):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "scenario_id": 2,
            "team_id": 2,
            "warcraftlogs_url": "https://www.warcraftlogs.com/reports/test2",
        }
        raid = RaidCreate(**data)
        assert raid.scenario_id == 2
        assert raid.team_id == 2
        assert raid.warcraftlogs_url == data["warcraftlogs_url"]

    def test_raid_update_partial(self):
        data = {
            "scenario_id": 3,
            "warcraftlogs_url": "https://www.warcraftlogs.com/reports/test3",
        }
        raid = RaidUpdate(**data)
        assert raid.scenario_id == 3
        assert raid.scheduled_at is None
        assert raid.team_id is None
        assert raid.warcraftlogs_url == data["warcraftlogs_url"]

    def test_raid_response_serialization(self):
        now = datetime.utcnow()
        data = {
            "id": 1,
            "scheduled_at": now,
            "scenario_id": 1,
            "team_id": 1,
            "created_at": now,
            "updated_at": now,
            "warcraftlogs_url": "https://www.warcraftlogs.com/reports/test4",
        }
        raid = RaidResponse(**data)
        assert raid.id == 1
        assert raid.scheduled_at == now
        assert raid.scenario_id == 1
        assert raid.team_id == 1
        assert raid.created_at == now
        assert raid.updated_at == now
        assert raid.warcraftlogs_url == data["warcraftlogs_url"]
