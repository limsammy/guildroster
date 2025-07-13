from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.token import Token
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserCreate,
    UserUpdate,
    UserLogin,
)
from app.utils.auth import require_any_token, security, require_superuser
from app.utils.password import get_password_hash, verify_password
from app.utils.logger import get_logger

logger = get_logger(__name__)

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
    hashed_password = get_password_hash(user_data.password)

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


@router.post("/login")
def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a token.

    **Returns:**
    - Token for authenticated user
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
    if not user.is_active:  # type: ignore[truthy-bool]
        logger.warning(
            f"Login failed: inactive user {user_credentials.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a user token
    token = Token.create_user_token(user_id=user.id, name="Login Token")  # type: ignore[arg-type]
    db.add(token)
    db.commit()
    db.refresh(token)

    logger.info(f"User {user.username} logged in successfully")
    return {
        "access_token": token.key,
        "token_type": "bearer",
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
        users=[UserResponse.from_orm(user) for user in users], total=total
    )


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
        user.hashed_password = get_password_hash(user_data.password)  # type: ignore[assignment]

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
