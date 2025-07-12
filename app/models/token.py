from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import secrets

from app.database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    token_type = Column(String, nullable=False)  # "user", "system", "api"
    name = Column(String, nullable=True)  # "Frontend App", "Mobile App", etc.
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship
    user = relationship("User", back_populates="tokens")

    @classmethod
    def generate_key(cls, length: int = 32) -> str:
        """Generate a secure random token key."""
        return secrets.token_urlsafe(length)

    @classmethod
    def create_user_token(
        cls, user_id: int, name: str = None, expires_in_days: int = None
    ) -> "Token":
        """Create a new user token."""
        token = cls(
            key=cls.generate_key(),
            user_id=user_id,
            token_type="user",
            name=name,
        )
        if expires_in_days:
            token.expires_at = datetime.now() + timedelta(days=expires_in_days)
        return token

    @classmethod
    def create_system_token(
        cls, name: str, expires_in_days: int = None
    ) -> "Token":
        """Create a new system token."""
        token = cls(
            key=cls.generate_key(),
            user_id=None,
            token_type="system",
            name=name,
        )
        if expires_in_days:
            token.expires_at = datetime.now() + timedelta(days=expires_in_days)
        return token

    @classmethod
    def create_api_token(
        cls, name: str, expires_in_days: int = None
    ) -> "Token":
        """Create a new API token."""
        token = cls(
            key=cls.generate_key(),
            user_id=None,
            token_type="api",
            name=name,
        )
        if expires_in_days:
            token.expires_at = datetime.now() + timedelta(days=expires_in_days)
        return token

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the token is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
