from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Raid(Base):
    __tablename__ = "raids"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheduled_at = Column(DateTime, nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    warcraftlogs_url = Column(String(255), nullable=True)

    # Relationships
    team = relationship("Team", back_populates="raids")
    scenario = relationship("Scenario", back_populates="raids")
    attendance = relationship(
        "Attendance", back_populates="raid", cascade="all, delete-orphan"
    )
