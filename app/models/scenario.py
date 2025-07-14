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


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    raids = relationship(
        "Raid", back_populates="scenario", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("name != ''", name="ck_scenario_name_not_empty"),
    )
