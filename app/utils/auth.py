from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.token import Token
from app.models.user import User
from app.models.session import Session as SessionModel
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


def get_current_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[Token]:
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
    logger.debug("No valid token found in header or cookie")
    return None


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get the current user from either token or session."""
    logger.debug("get_current_user called")

    # Try token-based auth first
    token = get_current_token(request, credentials, db)
    logger.debug(f"Token-based auth result: {token is not None}")
    if token and token.user_id is not None:
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
        logger.debug(f"Returning user from token: {user.username}")
        return user

    # Try session-based auth
    logger.debug("Trying session-based auth")
    session = get_session_from_cookie(request, db)
    logger.debug(f"Session-based auth result: {session is not None}")
    if session:
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
        logger.debug(f"Returning user from session: {user.username}")
        return user

    # No valid user found
    logger.debug("No valid user found")
    return None


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require a user session or valid token."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    logger.debug(f"require_user called with user: {user.username}")
    return user


def require_superuser(user: User = Depends(require_user)) -> User:
    """Require a superuser session or token."""
    logger.debug(f"require_superuser called with user: {user.username}")
    if user.is_superuser is False:
        logger.debug("User is not superuser, raising 403")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return user


def require_any_token(
    token: Optional[Token] = Depends(get_current_token),
) -> Token:
    logger.debug(
        f"require_any_token called with token type: {token.token_type if token else None}"
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
