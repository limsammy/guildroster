from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.token import Token
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)
# Configure security scheme for OpenAPI docs
security = HTTPBearer(
    auto_error=False,
    description="Enter your API token in the format: Bearer <token>",
    scheme_name="BearerAuth",
)


def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Token:
    """Get the current token from the Authorization header."""
    logger.debug(
        f"get_current_token called with credentials: {credentials.scheme if credentials else 'None'}"
    )

    if not credentials:
        logger.debug("No Authorization header provided, raising 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_key = credentials.credentials

    token = db.query(Token).filter(Token.key == token_key).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


def get_current_user(
    token: Token = Depends(get_current_token), db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user from the token."""
    if not token.user_id:
        # System or API token - no user associated
        return None

    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require a user token (not system/API token)."""
    logger.debug(
        f"require_user called with user: {user.username if user else 'None'}"
    )
    if not user:
        logger.debug("No user found, raising 403")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User token required",
        )
    return user


def require_superuser(user: User = Depends(require_user)) -> User:
    """Require a superuser token."""
    logger.debug(
        f"require_superuser called with user: {user.username if user else 'None'}"
    )
    if not user.is_superuser:
        logger.debug("User is not superuser, raising 403")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return user


def require_any_token(token: Token = Depends(get_current_token)) -> Token:
    """Require any valid token (user, system, or API token)."""
    logger.debug(
        f"require_any_token called with token type: {token.token_type}"
    )
    return token
