from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(8), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser_invite = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL = no expiration
    created_at = Column(DateTime, default=datetime.now)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship(
        "User", foreign_keys=[created_by], back_populates="created_invites"
    )
    used_user = relationship(
        "User", foreign_keys=[used_by], back_populates="used_invite"
    )
