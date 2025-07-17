from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(200), nullable=True)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    guild = relationship("Guild", back_populates="teams")
    creator = relationship("User", back_populates="created_teams")
    members = relationship("Member", back_populates="team")
    raids = relationship(
        "Raid", back_populates="team", cascade="all, delete-orphan"
    )
    toon_teams = relationship(
        "ToonTeam", back_populates="team", cascade="all, delete-orphan"
    )
    toons = relationship("Toon", secondary="toon_teams", back_populates="teams")

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", "guild_id", name="uq_team_name_guild"),
    )
