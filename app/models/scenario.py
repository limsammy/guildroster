from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    CheckConstraint,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

SCENARIO_DIFFICULTIES = ["Normal", "Heroic", "Celestial", "Challenge"]
SCENARIO_SIZES = ["10", "25"]


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(16), nullable=False)
    size = Column(String(4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    raids = relationship(
        "Raid", back_populates="scenario", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("TRIM(name) != ''", name="ck_scenario_name_not_empty"),
        CheckConstraint(
            f"difficulty IN ({', '.join([repr(d) for d in SCENARIO_DIFFICULTIES])})",
            name="ck_scenario_difficulty_valid",
        ),
        CheckConstraint(
            f"size IN ({', '.join([repr(s) for s in SCENARIO_SIZES])})",
            name="ck_scenario_size_valid",
        ),
    )
