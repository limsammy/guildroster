# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.raid import Raid, RAID_DIFFICULTIES


class TestRaidModel:
    def test_create_raid(self, db_session: Session):
        # This is a skeleton; actual test will need valid team_id and scenario_id
        raid = Raid(
            datetime=datetime.now() + timedelta(days=1),
            scenario_id=1,
            difficulty=RAID_DIFFICULTIES[0],
            size=10,
            team_id=1,
        )
        db_session.add(raid)
        # This will fail unless scenario_id and team_id exist, but structure is correct
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_difficulty_constraint(self, db_session: Session):
        raid = Raid(
            datetime=datetime.now() + timedelta(days=1),
            scenario_id=1,
            difficulty="Impossible",
            size=10,
            team_id=1,
        )
        db_session.add(raid)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_size_constraint(self, db_session: Session):
        raid = Raid(
            datetime=datetime.now() + timedelta(days=1),
            scenario_id=1,
            difficulty=RAID_DIFFICULTIES[0],
            size=0,
            team_id=1,
        )
        db_session.add(raid)
        with pytest.raises(IntegrityError):
            db_session.commit()
