from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List

from app.database import Base

# Allowed WoW classes
WOW_CLASSES = [
    "Death Knight",
    "Warrior",
    "Druid",
    "Paladin",
    "Monk",
    "Rogue",
    "Hunter",
    "Mage",
    "Warlock",
    "Priest",
    "Shaman",
]

# Allowed roles
WOW_ROLES = ["DPS", "Healer", "Tank"]


class Toon(Base):
    __tablename__ = "toons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)
    class_ = Column("class", String(20), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    attendance = relationship(
        "Attendance", back_populates="toon", cascade="all, delete-orphan"
    )
    toon_teams = relationship(
        "ToonTeam", back_populates="toon", cascade="all, delete-orphan"
    )
    teams = relationship(
        "Team",
        secondary="toon_teams",
        back_populates="toons",
        overlaps="toon_teams",
    )

    @property
    def team_ids(self) -> List[int]:
        """Get list of team IDs this toon belongs to."""
        return [team.id for team in self.teams]

    __table_args__ = (
        CheckConstraint(
            f"class IN ({', '.join([repr(c) for c in WOW_CLASSES])})",
            name="ck_toon_class_valid",
        ),
        CheckConstraint(
            f"role IN ({', '.join([repr(r) for r in WOW_ROLES])})",
            name="ck_toon_role_valid",
        ),
        # Only one main toon per member (enforced in code, not DB)
    )
