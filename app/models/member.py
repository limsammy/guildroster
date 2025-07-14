from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=True
    )  # Optional team assignment

    # Member profile fields
    display_name = Column(String(50), nullable=False)
    rank = Column(String(20), default="Member")  # Guild rank
    join_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit fields
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    guild = relationship("Guild", back_populates="members")
    team = relationship("Team", back_populates="members")
    # toons = relationship("Toon", back_populates="member", cascade="all, delete-orphan")
