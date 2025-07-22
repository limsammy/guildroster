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
    is_active = Column(Boolean, default=True, nullable=False)
    mop = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    raids = relationship(
        "Raid", back_populates="scenario", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("TRIM(name) != ''", name="ck_scenario_name_not_empty"),
    )

    @classmethod
    def get_variations(
        cls, scenario_name: str, mop: bool = False
    ) -> list[dict]:
        """
        Generate all variations for a given scenario name.
        Returns a list of dictionaries with name, difficulty, and size.

        Args:
            scenario_name: The name of the scenario
            mop: Whether this is a Mists of Pandaria scenario
                 - If True: All difficulties (Normal, Heroic, Celestial, Challenge)
                 - If False: Only Normal and Heroic difficulties
        """
        # Determine which difficulties to use based on MoP flag
        if mop:
            difficulties = SCENARIO_DIFFICULTIES  # All difficulties
        else:
            difficulties = ["Normal", "Heroic"]  # Only Normal and Heroic

        variations = []
        for difficulty in difficulties:
            for size in SCENARIO_SIZES:
                variations.append(
                    {
                        "name": scenario_name,
                        "difficulty": difficulty,
                        "size": size,
                        "display_name": f"{scenario_name} ({difficulty}, {size}-man)",
                    }
                )
        return variations

    @classmethod
    def get_variation_id(
        cls, scenario_name: str, difficulty: str, size: str
    ) -> str:
        """
        Generate a unique identifier for a scenario variation.
        This can be used to reference specific variations without storing them in the database.
        """
        return f"{scenario_name}|{difficulty}|{size}"

    @classmethod
    def parse_variation_id(cls, variation_id: str) -> dict:
        """
        Parse a variation ID back into its components.
        """
        parts = variation_id.split("|")
        if len(parts) != 3:
            raise ValueError(f"Invalid variation ID format: {variation_id}")
        return {"name": parts[0], "difficulty": parts[1], "size": parts[2]}
