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
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    warcraftlogs_url = Column(String(255), nullable=True)
    warcraftlogs_report_code = Column(String(50), nullable=True, index=True)
    warcraftlogs_metadata = Column(JSON, nullable=True)
    warcraftlogs_participants = Column(JSON, nullable=True)
    warcraftlogs_fights = Column(JSON, nullable=True)

    # Scenario information stored as JSON
    scenario_name = Column(String(100), nullable=False)
    scenario_difficulty = Column(String(16), nullable=False)
    scenario_size = Column(String(4), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="raids")
    attendance = relationship(
        "Attendance", back_populates="raid", cascade="all, delete-orphan"
    )

    @property
    def scenario_display_name(self) -> str:
        """Get the display name for the scenario variation."""
        return f"{self.scenario_name} ({self.scenario_difficulty}, {self.scenario_size}-man)"

    @property
    def scenario_variation_id(self) -> str:
        """Get the unique variation ID for this scenario."""
        from app.models.scenario import Scenario

        return Scenario.get_variation_id(
            self.scenario_name, self.scenario_difficulty, self.scenario_size
        )
