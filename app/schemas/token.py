from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenBase(BaseModel):
    token_type: str
    name: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


class TokenCreate(TokenBase):
    user_id: Optional[int] = None


class TokenResponse(TokenBase):
    id: int
    key: str
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenListResponse(BaseModel):
    tokens: list[TokenResponse]
    total: int


class TokenCreateResponse(BaseModel):
    token: TokenResponse
    message: str = "Token created successfully"
