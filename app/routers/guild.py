from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.guild import Guild
from app.models.user import User
from app.schemas.guild import GuildCreate, GuildUpdate, GuildResponse
from app.models.token import Token
from app.utils.auth import require_any_token, require_superuser

router = APIRouter(prefix="/guilds", tags=["Guilds"])


def get_guild_or_404(db: Session, guild_id: int) -> Guild:
    guild = db.query(Guild).filter(Guild.id == guild_id).first()
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    return guild


@router.post(
    "/",
    response_model=GuildResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_guild(
    guild_in: GuildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new guild. Superuser only.
    """
    # Check for unique name
    if db.query(Guild).filter(Guild.name == guild_in.name).first():
        raise HTTPException(status_code=400, detail="Guild name already exists")
    guild = Guild(
        name=guild_in.name,
        created_by=guild_in.created_by,
    )
    db.add(guild)
    db.commit()
    db.refresh(guild)
    return guild


@router.get(
    "/",
    response_model=List[GuildResponse],
    dependencies=[Depends(require_any_token)],
)
def list_guilds(
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    List all guilds. Any valid token required.
    """
    guilds = db.query(Guild).all()
    return guilds


@router.get(
    "/{guild_id}",
    response_model=GuildResponse,
    dependencies=[Depends(require_any_token)],
)
def get_guild(
    guild_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Get a guild by ID. Any valid token required.
    """
    guild = get_guild_or_404(db, guild_id)
    return guild


@router.put(
    "/{guild_id}",
    response_model=GuildResponse,
    dependencies=[Depends(require_superuser)],
)
def update_guild(
    guild_id: int,
    guild_in: GuildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a guild. Superuser only.
    """
    guild = get_guild_or_404(db, guild_id)
    if guild_in.name:
        # Check for unique name
        if (
            db.query(Guild)
            .filter(Guild.name == guild_in.name, Guild.id != guild_id)
            .first()
        ):
            raise HTTPException(
                status_code=400, detail="Guild name already exists"
            )
        guild.name = guild_in.name
    db.commit()
    db.refresh(guild)
    return guild


@router.delete(
    "/{guild_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_guild(
    guild_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a guild. Superuser only.
    """
    guild = get_guild_or_404(db, guild_id)
    db.delete(guild)
    db.commit()
    return None
