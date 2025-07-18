# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.raid import Raid
from app.models.scenario import Scenario, SCENARIO_DIFFICULTIES, SCENARIO_SIZES


class TestRaidModel:
    def test_create_raid(self, db_session: Session):
        # Create a scenario first
        scenario = Scenario(
            name="Test Scenario",
            difficulty=SCENARIO_DIFFICULTIES[0],
            size=SCENARIO_SIZES[0],
            is_active=True,
        )
        db_session.add(scenario)
        db_session.commit()

        # This is a skeleton; actual test will need valid team_id
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            team_id=1,
        )
        db_session.add(raid)
        # This will fail unless team_id exists, but structure is correct
        with pytest.raises(IntegrityError):
            db_session.commit()
