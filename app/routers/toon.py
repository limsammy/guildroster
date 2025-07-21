from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.toon import Toon
from app.models.team import Team
from app.models.toon_team import ToonTeam
from app.schemas.toon import ToonCreate, ToonUpdate, ToonResponse
from app.models.token import Token
from app.models.user import User
from app.utils.auth import require_user, require_superuser

router = APIRouter(prefix="/toons", tags=["Toons"])


def get_toon_or_404(db: Session, toon_id: int) -> Toon:
    toon = db.query(Toon).filter(Toon.id == toon_id).first()
    if not toon:
        raise HTTPException(status_code=404, detail="Toon not found")
    return toon


def update_toon_teams(
    db: Session, toon_id: int, team_ids: Optional[List[int]] = None
):
    """Update team assignments for a toon."""
    if team_ids is None:
        return

    # Remove existing team assignments
    db.query(ToonTeam).filter(ToonTeam.toon_id == toon_id).delete()

    # Add new team assignments
    for team_id in team_ids:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=400, detail=f"Team with ID {team_id} not found."
            )

        # Check if toon is already assigned to this team
        existing = (
            db.query(ToonTeam)
            .filter(ToonTeam.toon_id == toon_id, ToonTeam.team_id == team_id)
            .first()
        )

        if not existing:
            toon_team = ToonTeam(toon_id=toon_id, team_id=team_id)
            db.add(toon_team)


@router.post(
    "/",
    response_model=ToonResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_toon(
    toon_in: ToonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    toon = Toon(
        username=toon_in.username,
        class_=toon_in.class_,
        role=toon_in.role,
        is_main=toon_in.is_main,
    )
    db.add(toon)
    db.commit()
    db.refresh(toon)

    # Handle team assignments
    if toon_in.team_ids:
        update_toon_teams(db, toon.id, toon_in.team_ids)  # type: ignore[arg-type]
        db.commit()
        db.refresh(toon)

    return toon


@router.get(
    "/",
    response_model=List[ToonResponse],
)
def list_toons(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    return db.query(Toon).all()


@router.get(
    "/{toon_id}",
    response_model=ToonResponse,
)
def get_toon(
    toon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    toon = get_toon_or_404(db, toon_id)
    return toon


@router.put(
    "/{toon_id}",
    response_model=ToonResponse,
    dependencies=[Depends(require_superuser)],
)
def update_toon(
    toon_id: int,
    toon_in: ToonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    toon = get_toon_or_404(db, toon_id)
    if toon_in.username and toon_in.username != toon.username:
        toon.username = toon_in.username  # type: ignore[assignment]
    if toon_in.class_:
        toon.class_ = toon_in.class_  # type: ignore[assignment]
    if toon_in.role:
        toon.role = toon_in.role  # type: ignore[assignment]
    if toon_in.is_main is not None:
        toon.is_main = toon_in.is_main  # type: ignore[assignment]

    # Handle team assignments
    if toon_in.team_ids is not None:
        update_toon_teams(db, toon_id, toon_in.team_ids)

    db.commit()
    db.refresh(toon)
    return toon


@router.delete(
    "/{toon_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_toon(
    toon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    toon = get_toon_or_404(db, toon_id)
    db.delete(toon)
    db.commit()
    return None
