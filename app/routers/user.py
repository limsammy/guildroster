from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.token import Token
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserRegistration,
)
from app.utils.auth import (
    require_any_token,
    require_user,
    require_superuser,
    security,
)
from app.utils.password import hash_password, verify_password
from app.utils.invite import use_invite_code
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("User router loaded")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new user (superuser only).

    **Authentication:**
    - Requires superuser token
    """
    logger.info(
        f"Creating user {user_data.username} by superuser {current_user.username}"
    )

    # Check if username already exists
    existing_user = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create user
    user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User {user.username} created successfully")
    return user


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db),
):
    """
    Register a new user using an invite code.

    **Authentication:**
    - No authentication required (public endpoint)
    """
    logger.info(f"Registration attempt for user: {user_data.username}")

    # Check if username already exists
    existing_user = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Validate the invite code (but don't use it yet)
    from app.models.invite import Invite
    from app.utils.invite import validate_invite_code

    try:
        invite = validate_invite_code(user_data.invite_code, db)
    except HTTPException as e:
        logger.warning(
            f"Registration failed: invalid invite code {user_data.invite_code}"
        )
        raise e

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create user
    user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,  # New registrations are never superusers
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Now mark the invite code as used by this user
    invite.used_by = user.id
    invite.used_at = datetime.now()
    db.commit()

    logger.info(
        f"User {user.username} registered successfully using invite code {user_data.invite_code}"
    )
    return user


@router.post("/login")
def login_user(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a token.

    **Returns:**
    - Token for authenticated user
    - Sets HTTP-only cookie for session management
    """
    logger.debug(f"Login attempt for user: {user_credentials.username}")

    # Find user by username
    user = (
        db.query(User)
        .filter(User.username == user_credentials.username)
        .first()
    )
    if not user:
        logger.warning(
            f"Login failed: user {user_credentials.username} not found"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):  # type: ignore[arg-type]
        logger.warning(
            f"Login failed: incorrect password for user {user_credentials.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if user.is_active is False:
        logger.warning(
            f"Login failed: inactive user {user_credentials.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Create a session
    from app.models.session import Session as SessionModel

    session = SessionModel.create_session(user_id=user.id)  # type: ignore
    db.add(session)
    db.commit()
    db.refresh(session)

    # Set HTTP-only cookie for session management
    response.set_cookie(
        key="session_id",
        value=session.session_id,  # type: ignore
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=3600 * 24 * 7,  # 7 days
        path="/",
        domain=None,  # Let browser set the domain
    )

    logger.info(f"Set session cookie for user {user.username}")

    logger.info(f"User {user.username} logged in successfully")
    return {
        "user_id": user.id,
        "username": user.username,
        "is_superuser": user.is_superuser,
    }


@router.get(
    "/", response_model=UserListResponse, dependencies=[Depends(security)]
)
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Retrieve a paginated list of users.

    **Parameters:**
    - `skip`: Number of users to skip (for pagination)
    - `limit`: Maximum number of users to return (max 100)

    **Returns:**
    - List of users with total count

    **Authentication:**
    - Requires any valid token (user, system, or API)
    """
    logger.debug(f"Getting users with skip={skip}, limit={limit}")
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users], total=total
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(require_user),
):
    """
    Get current user information from session.
    """
    return current_user


@router.get(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(security)]
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Retrieve a specific user by ID.
    """
    logger.debug(f"Getting user by ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get(
    "/username/{username}",
    response_model=UserResponse,
    dependencies=[Depends(security)],
)
def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Retrieve a specific user by username.
    """
    logger.debug(f"Getting user by username: {username}")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a user (superuser only).

    **Authentication:**
    - Requires superuser token
    """
    logger.info(f"Updating user {user_id} by superuser {current_user.username}")

    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields if provided
    if user_data.username is not None:
        # Check if new username already exists
        existing_user = (
            db.query(User)
            .filter(User.username == user_data.username, User.id != user_id)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        user.username = user_data.username  # type: ignore[assignment]

    if user_data.password is not None:
        user.hashed_password = hash_password(user_data.password)  # type: ignore[assignment]

    if user_data.is_active is not None:
        user.is_active = user_data.is_active  # type: ignore[assignment]

    if user_data.is_superuser is not None:
        user.is_superuser = user_data.is_superuser  # type: ignore[assignment]

    db.commit()
    db.refresh(user)

    logger.info(f"User {user.username} updated successfully")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a user (superuser only).

    **Authentication:**
    - Requires superuser token
    """
    logger.info(f"Deleting user {user_id} by superuser {current_user.username}")

    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:  # type: ignore[truthy-bool]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db.delete(user)
    db.commit()

    logger.info(f"User {user.username} deleted successfully")
    return {"message": "User deleted successfully"}


@router.post("/logout")
def logout_user(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Logout current user by clearing the session.
    """
    # Get the current session and deactivate it
    from app.models.session import Session as SessionModel

    session_id = request.cookies.get("session_id")
    if session_id:
        session = (
            db.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        if session:
            session.is_active = False  # type: ignore
            db.commit()
            logger.info(f"Deactivated session for user {session.user_id}")

    # Clear the session cookie
    response.delete_cookie(key="session_id", path="/")

    return {"message": "Logged out successfully"}
