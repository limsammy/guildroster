from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import secrets
from typing import Optional

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")

    @classmethod
    def generate_session_id(cls, length: int = 32) -> str:
        """Generate a secure random session ID."""
        return secrets.token_urlsafe(length)

    @classmethod
    def create_session(
        cls,
        user_id: int,
        expires_in_days: int = 7,
    ) -> "Session":
        """Create a new session for a user."""
        session = cls(
            session_id=cls.generate_session_id(),
            user_id=user_id,
            expires_at=datetime.now() + timedelta(days=expires_in_days),
            is_active=True,
        )
        return session

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        now = datetime.now()
        return now > self.expires_at  # type: ignore

    def is_valid(self) -> bool:
        """Check if the session is valid (active and not expired)."""
        return bool(self.is_active) and not self.is_expired()
