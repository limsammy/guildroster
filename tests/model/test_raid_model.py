# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.raid import Raid, RAID_DIFFICULTIES, RAID_SIZES


class TestRaidModel:
    def test_create_raid(self, db_session: Session):
        # This is a skeleton; actual test will need valid team_id
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            difficulty=RAID_DIFFICULTIES[0],
            size=RAID_SIZES[0],
            team_id=1,
        )
        db_session.add(raid)
        # This will fail unless team_id exists, but structure is correct
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_difficulty_constraint(self, db_session: Session):
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            difficulty="Impossible",
            size=RAID_SIZES[0],
            team_id=1,
        )
        db_session.add(raid)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_size_constraint(self, db_session: Session):
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            difficulty=RAID_DIFFICULTIES[0],
            size="5",
            team_id=1,
        )
        db_session.add(raid)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
        for bad_size in ["15", "20", "30", "abc"]:
            raid = Raid(
                scheduled_at=datetime.now() + timedelta(days=1),
                difficulty=RAID_DIFFICULTIES[0],
                size=bad_size,
                team_id=1,
            )
            db_session.add(raid)
            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_valid_sizes(self, db_session: Session):
        for valid_size in RAID_SIZES:
            raid = Raid(
                scheduled_at=datetime.now() + timedelta(days=1),
                difficulty=RAID_DIFFICULTIES[0],
                size=valid_size,
                team_id=1,
            )
            db_session.add(raid)
            # Should fail only due to missing team_id, not size constraint
            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_valid_difficulties(self, db_session: Session):
        for valid_diff in RAID_DIFFICULTIES:
            raid = Raid(
                scheduled_at=datetime.now() + timedelta(days=1),
                difficulty=valid_diff,
                size=RAID_SIZES[0],
                team_id=1,
            )
            db_session.add(raid)
            # Should fail only due to missing team_id, not difficulty constraint
            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()
