from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserListResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=UserListResponse)
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of users with pagination.
    """
    logger.debug(f"Getting users with skip={skip}, limit={limit}")
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()

    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users], total=total
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
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


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
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
