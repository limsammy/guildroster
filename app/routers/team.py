from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.team import Team
from app.models.guild import Guild
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.models.token import Token
from app.utils.auth import require_user, require_superuser

router = APIRouter(prefix="/teams", tags=["Teams"])


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


def get_guild_or_404(db: Session, guild_id: int) -> Guild:
    guild = db.query(Guild).filter(Guild.id == guild_id).first()
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    return guild


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new team. Superuser only.
    """
    # Verify guild exists
    guild = get_guild_or_404(db, team_in.guild_id)

    # Check for unique name within the guild
    if (
        db.query(Team)
        .filter(Team.name == team_in.name, Team.guild_id == team_in.guild_id)
        .first()
    ):
        raise HTTPException(
            status_code=400, detail="Team name already exists in this guild"
        )

    team = Team(
        name=team_in.name,
        description=team_in.description,
        guild_id=team_in.guild_id,
        created_by=current_user.id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get(
    "/",
    response_model=List[TeamResponse],
)
def list_teams(
    guild_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    List teams. Can filter by guild_id. Any valid token required.
    """
    query = db.query(Team)
    if guild_id:
        query = query.filter(Team.guild_id == guild_id)
    teams = query.all()
    return teams


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get a team by ID. Any valid token required.
    """
    team = get_team_or_404(db, team_id)
    return team


@router.get(
    "/guild/{guild_id}",
    response_model=List[TeamResponse],
)
def get_teams_by_guild(
    guild_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all teams for a specific guild. Any valid token required.
    """
    guild = get_guild_or_404(db, guild_id)
    teams = db.query(Team).filter(Team.guild_id == guild_id).all()
    return teams


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    dependencies=[Depends(require_superuser)],
)
def update_team(
    team_id: int,
    team_in: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a team. Superuser only.
    """
    team = get_team_or_404(db, team_id)

    if team_in.name:
        # Check for unique name within the guild
        if (
            db.query(Team)
            .filter(
                Team.name == team_in.name,
                Team.guild_id == team.guild_id,
                Team.id != team_id,
            )
            .first()
        ):
            raise HTTPException(
                status_code=400, detail="Team name already exists in this guild"
            )
        team.name = team_in.name  # type: ignore[assignment]

    if team_in.description is not None:
        team.description = team_in.description  # type: ignore[assignment]

    if team_in.is_active is not None:
        team.is_active = team_in.is_active  # type: ignore[assignment]

    db.commit()
    db.refresh(team)
    return team


@router.delete(
    "/{team_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a team. Superuser only.
    """
    team = get_team_or_404(db, team_id)
    db.delete(team)
    db.commit()
    return None
