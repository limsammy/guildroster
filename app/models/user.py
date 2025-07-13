from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # invite_code = Column(String, ForeignKey("invites.code"))
    # invite = relationship("Invite", back_populates="users")

    # guilds = relationship("Guild", back_populates="members")
    guilds = relationship(
        "Guild", back_populates="creator", cascade="all, delete-orphan"
    )

    tokens = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
