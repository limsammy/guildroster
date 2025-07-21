from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.session import Session as SessionModel
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_session_from_cookie(
    request: Request, db: Session = Depends(get_db)
) -> Optional[SessionModel]:
    """Get session from session cookie."""
    session_id = request.cookies.get("session_id")
    logger.debug(f"Session ID from cookie: {session_id}")
    if not session_id:
        logger.debug("No session ID found in cookie")
        return None

    session = (
        db.query(SessionModel)
        .filter(SessionModel.session_id == session_id)
        .first()
    )
    if not session:
        logger.debug("No session found in database")
        return None

    if not session.is_valid():
        logger.debug("Session is invalid")
        return None

    logger.debug(f"Valid session found: user_id={session.user_id}")
    return session


def get_current_session(
    request: Request,
    db: Session = Depends(get_db),
) -> SessionModel:
    """Get the current session from cookie."""
    session = get_session_from_cookie(request, db)
    if not session:
        logger.debug("No valid session found, raising 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return session


def get_current_user(
    session: SessionModel = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    """Get the current user from the session."""
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user


def require_user(user: User = Depends(get_current_user)) -> User:
    """Require a user session."""
    logger.debug(f"require_user called with user: {user.username}")
    return user


def require_superuser(user: User = Depends(require_user)) -> User:
    """Require a superuser session."""
    logger.debug(f"require_superuser called with user: {user.username}")
    if user.is_superuser is False:
        logger.debug("User is not superuser, raising 403")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return user
