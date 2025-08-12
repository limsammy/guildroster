from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.token import Token
from app.models.user import User
from app.schemas.token import (
    TokenCreate,
    TokenResponse,
    TokenListResponse,
    TokenCreateResponse,
)
from app.utils.auth import require_superuser
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Token router loaded")

router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TokenCreateResponse)
def create_token(
    token_data: TokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Create a new token (superuser only)."""
    logger.info(
        f"Creating {token_data.token_type} token by user {current_user.username}"
    )
    # Validate token type
    if token_data.token_type not in ["user", "system", "api"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type. Must be 'user', 'system', or 'api'",
        )

    # Validate user_id for user tokens
    if token_data.token_type == "user" and not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required for user tokens",
        )

    # Validate user exists for user tokens
    if token_data.token_type == "user" and token_data.user_id:
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    # Create token based on type
    if token_data.token_type == "user":
        token = Token.create_user_token(
            user_id=token_data.user_id, name=token_data.name  # type: ignore[arg-type]
        )
    elif token_data.token_type == "system":
        token = Token.create_system_token(name=token_data.name)
    else:  # api
        token = Token.create_api_token(name=token_data.name)

    # Set additional fields
    if token_data.expires_at:
        token.expires_at = token_data.expires_at  # type: ignore[assignment]
    token.is_active = token_data.is_active  # type: ignore[assignment]

    db.add(token)
    db.commit()
    db.refresh(token)

    return TokenCreateResponse(token=token)


@router.get("/", response_model=TokenListResponse)
def get_tokens(
    skip: int = 0,
    limit: int = 100,
    token_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Get list of tokens (superuser only)."""
    query = db.query(Token)

    if token_type:
        if token_type not in ["user", "system", "api"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )
        query = query.filter(Token.token_type == token_type)

    tokens = query.offset(skip).limit(limit).all()
    total = query.count()

    return TokenListResponse(tokens=tokens, total=total)  # type: ignore[arg-type]


@router.get("/{token_id}", response_model=TokenResponse)
def get_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Get a specific token by ID (superuser only)."""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )
    return token


@router.delete("/{token_id}")
def delete_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Delete a token (superuser only)."""
    logger.info(f"Deleting token {token_id} by user {current_user.username}")
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    db.delete(token)
    db.commit()

    return {"message": "Token deleted successfully"}


@router.post("/{token_id}/deactivate")
def deactivate_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Deactivate a token (superuser only)."""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    token.is_active = False  # type: ignore[assignment]
    db.commit()

    return {"message": "Token deactivated successfully"}


@router.post("/{token_id}/activate")
def activate_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Activate a token (superuser only)."""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    token.is_active = True  # type: ignore[assignment]
    db.commit()

    return {"message": "Token activated successfully"}
