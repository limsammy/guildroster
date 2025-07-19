from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    JSON,
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
    warcraftlogs_report_code = Column(String(50), nullable=True, index=True)
    warcraftlogs_metadata = Column(JSON, nullable=True)
    warcraftlogs_participants = Column(JSON, nullable=True)
    warcraftlogs_fights = Column(JSON, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="raids")
    scenario = relationship("Scenario", back_populates="raids")
    attendance = relationship(
        "Attendance", back_populates="raid", cascade="all, delete-orphan"
    )
