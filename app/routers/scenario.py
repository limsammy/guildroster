from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
)
from app.models.token import Token
from app.utils.auth import require_user, require_superuser
from app.models.user import User
from app.utils.request_logger import log_request_context

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


def get_scenario_or_404(db: Session, scenario_id: int) -> Scenario:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post(
    "/",
    response_model=ScenarioResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_scenario(
    scenario_in: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new scenario. Superuser only.
    """
    scenario = Scenario(
        name=scenario_in.name,
        difficulty=scenario_in.difficulty,
        size=scenario_in.size,
        is_active=scenario_in.is_active,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.get(
    "/",
    response_model=List[ScenarioResponse],
)
def list_scenarios(
    request: Request,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    List scenarios. Can filter by is_active. Any valid token required.
    """
    log_request_context(
        request, f"Listing scenarios (active filter: {is_active})"
    )

    query = db.query(Scenario)
    if is_active is not None:
        query = query.filter(Scenario.is_active == is_active)
    scenarios = query.all()
    return scenarios


@router.get(
    "/active",
    response_model=List[ScenarioResponse],
)
def get_active_scenarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all active scenarios. Any valid token required.
    """
    scenarios = db.query(Scenario).filter(Scenario.is_active == True).all()
    return scenarios


@router.get(
    "/{scenario_id}",
    response_model=ScenarioResponse,
)
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get a scenario by ID. Any valid token required.
    """
    scenario = get_scenario_or_404(db, scenario_id)
    return scenario


@router.put(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    dependencies=[Depends(require_superuser)],
)
def update_scenario(
    scenario_id: int,
    scenario_in: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a scenario. Superuser only.
    """
    scenario = get_scenario_or_404(db, scenario_id)

    if scenario_in.name is not None:
        scenario.name = scenario_in.name  # type: ignore[assignment]

    if scenario_in.difficulty is not None:
        scenario.difficulty = scenario_in.difficulty  # type: ignore[assignment]

    if scenario_in.size is not None:
        scenario.size = scenario_in.size  # type: ignore[assignment]

    if scenario_in.is_active is not None:
        scenario.is_active = scenario_in.is_active  # type: ignore[assignment]

    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete(
    "/{scenario_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a scenario. Superuser only.
    """
    scenario = get_scenario_or_404(db, scenario_id)
    db.delete(scenario)
    db.commit()
    return None
