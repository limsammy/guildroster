from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.invite import Invite
from app.schemas.invite import (
    InviteResponse,
    InviteListResponse,
    InviteCreate,
)
from app.utils.auth import (
    require_user,
    require_superuser,
    security,
)
from app.utils.invite import (
    ensure_unique_code,
    calculate_expiration_date,
    is_invite_expired,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/invites",
    tags=["invites"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=InviteResponse)
def create_invite(
    invite_data: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Generate a new invite code (superuser only).

    **Parameters:**
    - `expires_in_days`: Days until expiration (None for no expiration)

    **Authentication:**
    - Requires superuser token
    """
    logger.info(
        f"Creating invite code by superuser {current_user.username} with expiration: {invite_data.expires_in_days} days"
    )

    # Generate unique code
    code = ensure_unique_code(db)

    # Calculate expiration date
    expires_at = calculate_expiration_date(invite_data.expires_in_days)

    # Create invite
    invite = Invite(
        code=code,
        created_by=current_user.id,
        expires_at=expires_at,
        is_superuser_invite=invite_data.is_superuser_invite,
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    # Add usernames for response
    invite.creator_username = current_user.username
    invite.is_expired = is_invite_expired(invite)

    logger.info(f"Invite code {code} created successfully")
    return invite


@router.get(
    "/", response_model=InviteListResponse, dependencies=[Depends(security)]
)
def get_invites(
    skip: int = Query(0, ge=0, description="Number of invites to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of invites to return"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all invite codes created by the current user.

    **Parameters:**
    - `skip`: Number of invites to skip (for pagination)
    - `limit`: Maximum number of invites to return (max 100)

    **Returns:**
    - List of invite codes with statistics

    **Authentication:**
    - Requires user token
    """
    logger.debug(
        f"Getting invites for user {current_user.username} with skip={skip}, limit={limit}"
    )

    # Get invites created by current user
    invites_query = db.query(Invite).filter(
        Invite.created_by == current_user.id
    )

    # Get total count
    total = invites_query.count()

    # Get paginated results
    invites = invites_query.offset(skip).limit(limit).all()

    # Add usernames and expiration status
    for invite in invites:
        invite.creator_username = current_user.username
        invite.is_expired = is_invite_expired(invite)

        # Add used username if applicable
        if invite.used_by:
            used_user = db.query(User).filter(User.id == invite.used_by).first()
            invite.used_username = used_user.username if used_user else None

    # Calculate statistics
    unused_count = (
        db.query(Invite)
        .filter(
            Invite.created_by == current_user.id,
            Invite.used_by.is_(None),
            Invite.is_active == True,
        )
        .count()
    )

    used_count = (
        db.query(Invite)
        .filter(
            Invite.created_by == current_user.id, Invite.used_by.is_not(None)
        )
        .count()
    )

    expired_count = (
        db.query(Invite)
        .filter(
            Invite.created_by == current_user.id,
            Invite.used_by.is_(None),
            Invite.is_active == True,
        )
        .count()
    )

    # Recalculate expired count properly
    expired_count = 0
    for invite in (
        db.query(Invite)
        .filter(
            Invite.created_by == current_user.id,
            Invite.used_by.is_(None),
            Invite.is_active == True,
        )
        .all()
    ):
        if is_invite_expired(invite):
            expired_count += 1

    return InviteListResponse(
        invites=[InviteResponse.model_validate(invite) for invite in invites],
        total=total,
        unused_count=unused_count,
        used_count=used_count,
        expired_count=expired_count,
    )


@router.get(
    "/{invite_id}",
    response_model=InviteResponse,
    dependencies=[Depends(security)],
)
def get_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get a specific invite code by ID.

    **Authentication:**
    - Requires user token (can only view own codes)
    """
    logger.debug(f"Getting invite {invite_id} for user {current_user.username}")

    invite = (
        db.query(Invite)
        .filter(Invite.id == invite_id, Invite.created_by == current_user.id)
        .first()
    )

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found"
        )

    # Add usernames and expiration status
    invite.creator_username = current_user.username
    invite.is_expired = is_invite_expired(invite)

    if invite.used_by:
        used_user = db.query(User).filter(User.id == invite.used_by).first()
        invite.used_username = used_user.username if used_user else None

    return invite


@router.delete("/{invite_id}")
def invalidate_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Invalidate an unused invite code.

    **Authentication:**
    - Requires user token (can only invalidate own codes)
    """
    logger.info(
        f"Invalidating invite {invite_id} by user {current_user.username}"
    )

    invite = (
        db.query(Invite)
        .filter(Invite.id == invite_id, Invite.created_by == current_user.id)
        .first()
    )

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found"
        )

    if invite.used_by is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invalidate a used invite code",
        )

    if not invite.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code is already invalidated",
        )

    invite.is_active = False
    db.commit()

    logger.info(f"Invite code {invite.code} invalidated successfully")
    return {"message": "Invite code invalidated successfully"}
