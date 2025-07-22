from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class ToonTeam(Base):
    __tablename__ = "toon_teams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    toon_id = Column(
        Integer, ForeignKey("toons.id"), nullable=False, index=True
    )
    team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    toon = relationship(
        "Toon", back_populates="toon_teams", overlaps="teams,toons"
    )
    team = relationship(
        "Team", back_populates="toon_teams", overlaps="teams,toons"
    )

    # Constraints
    __table_args__ = (
        # Ensure a toon can only be in a team once
        # This will be handled by a unique constraint in the migration
    )
