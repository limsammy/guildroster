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


def get_token_from_cookie(
    request: Request, db: Session = Depends(get_db)
) -> Optional[Token]:
    """Get token from session cookie."""
    session_token = request.cookies.get("session_token")
    logger.debug(f"Session token from cookie: {session_token}")
    if not session_token:
        logger.debug("No session token found in cookie")
        return None

    token = db.query(Token).filter(Token.key == session_token).first()
    if not token:
        logger.debug("No token found in database")
        return None

    if not token.is_valid():
        logger.debug("Token is invalid")
        return None

    logger.debug(
        f"Valid token found: type={token.token_type}, user_id={token.user_id}"
    )
    return token


def get_current_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Token:
    """Get the current token from either Authorization header or session cookie."""
    logger.debug(
        f"get_current_token called with credentials: {credentials.scheme if credentials else 'None'}"
    )

    # First try to get token from Authorization header
    if credentials:
        token_key = credentials.credentials
        token = db.query(Token).filter(Token.key == token_key).first()
        if token and token.is_valid():
            return token

    # If no valid header token, try cookie
    cookie_token = get_token_from_cookie(request, db)
    if cookie_token:
        return cookie_token

    # No valid token found
    logger.debug("No valid token found in header or cookie, raising 401")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Token = Depends(get_current_token), db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user from the token."""
    if token.user_id is None:
        # System or API token - no user associated
        return None

    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active is False:
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
    if user.is_superuser is False:
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
