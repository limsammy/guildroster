import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.invite import Invite
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_invite_code() -> str:
    """Generate a cryptographically secure 8-character alphanumeric code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def ensure_unique_code(db: Session, max_attempts: int = 10) -> str:
    """Generate a unique invite code, retrying if necessary."""
    for attempt in range(max_attempts):
        code = generate_invite_code()
        existing = db.query(Invite).filter(Invite.code == code).first()
        if not existing:
            return code

    # If we've exhausted attempts, raise an error
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unable to generate unique invite code after multiple attempts",
    )


def validate_invite_code(code: str, db: Session) -> Invite:
    """Validate an invite code and return the invite object."""
    # Normalize to uppercase
    code = code.upper()

    invite = db.query(Invite).filter(Invite.code == code).first()
    if not invite:
        logger.warning(f"Invalid invite code attempted: {code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code"
        )

    if not invite.is_active:
        logger.warning(f"Inactive invite code attempted: {code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has been invalidated",
        )

    if invite.used_by is not None:
        logger.warning(f"Used invite code attempted: {code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has already been used",
        )

    if invite.expires_at and invite.expires_at < datetime.now():
        logger.warning(f"Expired invite code attempted: {code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code has expired",
        )

    return invite


def use_invite_code(code: str, user_id: int, db: Session) -> None:
    """Mark an invite code as used by a specific user."""
    invite = validate_invite_code(code, db)
    invite.used_by = user_id
    invite.used_at = datetime.now()
    db.commit()
    logger.info(f"Invite code {code} used by user {user_id}")


def is_invite_expired(invite: Invite) -> bool:
    """Check if an invite code has expired."""
    if not invite.expires_at:
        return False
    return invite.expires_at < datetime.now()


def calculate_expiration_date(
    expires_in_days: Optional[int],
) -> Optional[datetime]:
    """Calculate expiration date based on days from now."""
    if expires_in_days is None:
        return None
    return datetime.now() + timedelta(days=expires_in_days)
