from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.raid import Raid
from app.models.team import Team
from app.schemas.raid import RaidCreate, RaidUpdate, RaidResponse
from app.models.token import Token
from app.utils.auth import require_any_token, require_superuser
from app.models.user import User

router = APIRouter(prefix="/raids", tags=["Raids"])


def get_raid_or_404(db: Session, raid_id: int) -> Raid:
    raid = db.query(Raid).filter(Raid.id == raid_id).first()
    if not raid:
        raise HTTPException(status_code=404, detail="Raid not found")
    return raid


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post(
    "/",
    response_model=RaidResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_raid(
    raid_in: RaidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new raid. Superuser only.
    """
    # Verify team exists
    team = get_team_or_404(db, raid_in.team_id)

    raid = Raid(
        scheduled_at=raid_in.scheduled_at,
        difficulty=raid_in.difficulty,
        size=raid_in.size,
        team_id=raid_in.team_id,
    )
    db.add(raid)
    db.commit()
    db.refresh(raid)
    return raid


@router.get(
    "/",
    response_model=List[RaidResponse],
    dependencies=[Depends(require_any_token)],
)
def list_raids(
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    List raids. Can filter by team_id. Any valid token required.
    """
    query = db.query(Raid)
    if team_id:
        query = query.filter(Raid.team_id == team_id)
    raids = query.all()
    return raids


@router.get(
    "/{raid_id}",
    response_model=RaidResponse,
    dependencies=[Depends(require_any_token)],
)
def get_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Get a raid by ID. Any valid token required.
    """
    raid = get_raid_or_404(db, raid_id)
    return raid


@router.get(
    "/team/{team_id}",
    response_model=List[RaidResponse],
    dependencies=[Depends(require_any_token)],
)
def get_raids_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Get all raids for a specific team. Any valid token required.
    """
    team = get_team_or_404(db, team_id)
    raids = db.query(Raid).filter(Raid.team_id == team_id).all()
    return raids


@router.put(
    "/{raid_id}",
    response_model=RaidResponse,
    dependencies=[Depends(require_superuser)],
)
def update_raid(
    raid_id: int,
    raid_in: RaidUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a raid. Superuser only.
    """
    raid = get_raid_or_404(db, raid_id)

    if raid_in.scheduled_at is not None:
        raid.scheduled_at = raid_in.scheduled_at  # type: ignore[assignment]

    if raid_in.difficulty is not None:
        raid.difficulty = raid_in.difficulty  # type: ignore[assignment]

    if raid_in.size is not None:
        raid.size = raid_in.size  # type: ignore[assignment]

    if raid_in.team_id is not None:
        # Verify new team exists
        team = get_team_or_404(db, raid_in.team_id)
        raid.team_id = raid_in.team_id  # type: ignore[assignment]

    db.commit()
    db.refresh(raid)
    return raid


@router.delete(
    "/{raid_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a raid. Superuser only.
    """
    raid = get_raid_or_404(db, raid_id)
    db.delete(raid)
    db.commit()
    return None
