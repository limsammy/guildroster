from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

RAID_DIFFICULTIES = ["Normal", "Heroic", "Celestial", "Challenge"]
RAID_SIZES = ["10", "25"]


class Raid(Base):
    __tablename__ = "raids"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheduled_at = Column(DateTime, nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    difficulty = Column(String(16), nullable=False)
    size = Column(String(4), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    team = relationship("Team", back_populates="raids")
    scenario = relationship("Scenario", back_populates="raids")
    attendance = relationship(
        "Attendance", back_populates="raid", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            f"difficulty IN ({', '.join([repr(d) for d in RAID_DIFFICULTIES])})",
            name="ck_raid_difficulty_valid",
        ),
        CheckConstraint(
            f"size IN ({', '.join([repr(s) for s in RAID_SIZES])})",
            name="ck_raid_size_valid",
        ),
    )
