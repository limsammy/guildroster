import pytest
from datetime import datetime, timedelta
from app.schemas.raid import (
    RaidBase,
    RaidCreate,
    RaidUpdate,
    RaidResponse,
)
from app.models.raid import RAID_DIFFICULTIES, RAID_SIZES


class TestRaidSchemas:
    def test_raid_base_valid(self):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "difficulty": RAID_DIFFICULTIES[0],
            "size": RAID_SIZES[0],
            "team_id": 1,
        }
        raid = RaidBase(**data)
        assert raid.scheduled_at == data["scheduled_at"]
        assert raid.difficulty == RAID_DIFFICULTIES[0]
        assert raid.size == RAID_SIZES[0]
        assert raid.team_id == 1

    @pytest.mark.parametrize("bad_diff", ["", "Impossible", "normal", "Mythic"])
    def test_raid_base_invalid_difficulty(self, bad_diff):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "difficulty": bad_diff,
            "size": RAID_SIZES[0],
            "team_id": 1,
        }
        with pytest.raises(ValueError):
            RaidBase(**data)

    @pytest.mark.parametrize("bad_size", ["", "5", "15", "20", "30", "abc"])
    def test_raid_base_invalid_size(self, bad_size):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "difficulty": RAID_DIFFICULTIES[0],
            "size": bad_size,
            "team_id": 1,
        }
        with pytest.raises(ValueError):
            RaidBase(**data)

    def test_raid_create(self):
        data = {
            "scheduled_at": datetime.now() + timedelta(days=1),
            "difficulty": RAID_DIFFICULTIES[1],
            "size": RAID_SIZES[1],
            "team_id": 2,
        }
        raid = RaidCreate(**data)
        assert raid.difficulty == RAID_DIFFICULTIES[1]
        assert raid.size == RAID_SIZES[1]
        assert raid.team_id == 2

    def test_raid_update_partial(self):
        data = {"difficulty": RAID_DIFFICULTIES[2]}
        raid = RaidUpdate(**data)
        assert raid.difficulty == RAID_DIFFICULTIES[2]
        assert raid.scheduled_at is None
        assert raid.size is None
        assert raid.team_id is None

    def test_raid_update_invalid(self):
        # Only set the field being tested, and use correct types
        with pytest.raises(ValueError):
            RaidUpdate(difficulty="Impossible")
        with pytest.raises(ValueError):
            RaidUpdate(size="abc")

    def test_raid_response_serialization(self):
        now = datetime.utcnow()
        data = {
            "id": 1,
            "scheduled_at": now,
            "difficulty": RAID_DIFFICULTIES[0],
            "size": RAID_SIZES[0],
            "team_id": 1,
            "created_at": now,
            "updated_at": now,
        }
        raid = RaidResponse(**data)
        assert raid.id == 1
        assert raid.scheduled_at == now
        assert raid.difficulty == RAID_DIFFICULTIES[0]
        assert raid.size == RAID_SIZES[0]
        assert raid.team_id == 1
        assert raid.created_at == now
        assert raid.updated_at == now
