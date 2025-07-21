# type: ignore[comparison-overlap,assignment]
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.member import Member
from app.models.guild import Guild
from app.models.team import Team
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from app.models.token import Token
from app.utils.auth import require_user, require_superuser

router = APIRouter(prefix="/members", tags=["Members"])


def get_member_or_404(db: Session, member_id: int) -> Member:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def get_guild_or_404(db: Session, guild_id: int) -> Guild:
    guild = db.query(Guild).filter(Guild.id == guild_id).first()
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    return guild


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new member. Superuser only.
    """
    # Verify guild exists
    guild = get_guild_or_404(db, member_in.guild_id)

    # Check for unique display name within the guild
    if (
        db.query(Member)
        .filter(
            Member.display_name == member_in.display_name,
            Member.guild_id == member_in.guild_id,
        )
        .first()
    ):
        raise HTTPException(
            status_code=400,
            detail="Member display name already exists in this guild",
        )

    member = Member(
        display_name=member_in.display_name,
        rank=member_in.rank,
        guild_id=member_in.guild_id,
        join_date=member_in.join_date,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get(
    "/",
    response_model=List[MemberResponse],
)
def list_members(
    guild_id: Optional[int] = None,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    List members. Can filter by guild_id or team_id. Any valid token required.
    """
    query = db.query(Member)
    if guild_id is not None:
        query = query.filter(Member.guild_id == guild_id)
    if team_id is not None:
        query = query.filter(Member.team_id == team_id)
    members = query.all()
    return members


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get a member by ID. Any valid token required.
    """
    member = get_member_or_404(db, member_id)
    return member


@router.get(
    "/guild/{guild_id}",
    response_model=List[MemberResponse],
)
def get_members_by_guild(
    guild_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all members for a specific guild. Any valid token required.
    """
    guild = get_guild_or_404(db, guild_id)
    members = db.query(Member).filter(Member.guild_id == guild_id).all()
    return members


@router.get(
    "/team/{team_id}",
    response_model=List[MemberResponse],
)
def get_members_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all members for a specific team. Any valid token required.
    """
    team = get_team_or_404(db, team_id)
    members = db.query(Member).filter(Member.team_id == team_id).all()
    return members


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    dependencies=[Depends(require_superuser)],
)
def update_member(
    member_id: int,
    member_in: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a member. Superuser only.
    """
    member = get_member_or_404(db, member_id)

    if member_in.display_name:
        # Check for unique display name within the guild
        if (
            db.query(Member)
            .filter(
                Member.display_name == member_in.display_name,
                Member.guild_id == member.guild_id,
                Member.id != member_id,
            )
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail="Member display name already exists in this guild",
            )
        member.display_name = member_in.display_name  # type: ignore[assignment]

    if member_in.rank is not None:
        member.rank = member_in.rank  # type: ignore[assignment]

    if member_in.team_id is not None:
        if member_in.team_id == 0:  # Allow setting to None by passing 0
            member.team_id = None  # type: ignore[assignment]
        else:
            # Verify team exists and belongs to the same guild
            team = get_team_or_404(db, member_in.team_id)
            if team.guild_id != member.guild_id:
                raise HTTPException(
                    status_code=400,
                    detail="Team does not belong to the member's guild",
                )
            member.team_id = member_in.team_id  # type: ignore[assignment]

    if member_in.is_active is not None:
        member.is_active = member_in.is_active  # type: ignore[assignment]

    db.commit()
    db.refresh(member)
    return member


@router.delete(
    "/{member_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a member. Superuser only.
    """
    member = get_member_or_404(db, member_id)
    db.delete(member)
    db.commit()
    return None
