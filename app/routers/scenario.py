from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioWithVariations,
    ScenarioVariation,
    RaidScenarioInfo,
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
    Create a new scenario template. This will automatically generate all variations based on the MoP flag:
    - If MoP is True: All difficulties (Normal, Heroic, Celestial, Challenge) × 2 sizes = 8 variations
    - If MoP is False: Only Normal and Heroic difficulties × 2 sizes = 4 variations
    Superuser only.
    """
    # Check if scenario with this name already exists
    existing = (
        db.query(Scenario).filter(Scenario.name == scenario_in.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Scenario with name '{scenario_in.name}' already exists",
        )

    scenario = Scenario(
        name=scenario_in.name,
        is_active=scenario_in.is_active,
        mop=scenario_in.mop,
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
    List scenario templates. Can filter by is_active. Any valid token required.
    """
    log_request_context(
        request, f"Listing scenario templates (active filter: {is_active})"
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
    Get all active scenario templates. Any valid token required.
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
    Get a scenario template by ID. Any valid token required.
    """
    scenario = get_scenario_or_404(db, scenario_id)
    return scenario


@router.get(
    "/{scenario_id}/variations",
    response_model=ScenarioWithVariations,
)
def get_scenario_variations(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all variations for a scenario template. Any valid token required.
    """
    scenario = get_scenario_or_404(db, scenario_id)

    # Generate variations for this scenario using the MoP flag
    variations_data = Scenario.get_variations(scenario.name, scenario.mop)
    variations = []

    for var_data in variations_data:
        variation = ScenarioVariation(
            name=var_data["name"],
            difficulty=var_data["difficulty"],
            size=var_data["size"],
            display_name=var_data["display_name"],
            variation_id=Scenario.get_variation_id(
                var_data["name"], var_data["difficulty"], var_data["size"]
            ),
        )
        variations.append(variation)

    return ScenarioWithVariations(
        id=scenario.id,
        name=scenario.name,
        is_active=scenario.is_active,
        mop=scenario.mop,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at,
        variations=variations,
    )


@router.get(
    "/variations/all",
    response_model=List[ScenarioVariation],
)
def get_all_variations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all scenario variations from all active scenario templates. Any valid token required.
    """
    active_scenarios = (
        db.query(Scenario).filter(Scenario.is_active == True).all()
    )
    all_variations = []

    for scenario in active_scenarios:
        variations_data = Scenario.get_variations(scenario.name, scenario.mop)
        for var_data in variations_data:
            variation = ScenarioVariation(
                name=var_data["name"],
                difficulty=var_data["difficulty"],
                size=var_data["size"],
                display_name=var_data["display_name"],
                variation_id=Scenario.get_variation_id(
                    var_data["name"], var_data["difficulty"], var_data["size"]
                ),
            )
            all_variations.append(variation)

    return all_variations


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
    Update a scenario template. Superuser only.
    """
    scenario = get_scenario_or_404(db, scenario_id)

    if scenario_in.name is not None:
        # Check if the new name conflicts with an existing scenario
        existing = (
            db.query(Scenario)
            .filter(
                Scenario.name == scenario_in.name, Scenario.id != scenario_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Scenario with name '{scenario_in.name}' already exists",
            )
        scenario.name = scenario_in.name

    if scenario_in.is_active is not None:
        scenario.is_active = scenario_in.is_active

    if scenario_in.mop is not None:
        scenario.mop = scenario_in.mop

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
    Delete a scenario template. Superuser only.
    """
    scenario = get_scenario_or_404(db, scenario_id)
    db.delete(scenario)
    db.commit()
    return None
