from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Enum,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    BENCHED = "benched"


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    raid_id = Column(
        Integer, ForeignKey("raids.id"), nullable=False, index=True
    )
    toon_id = Column(
        Integer, ForeignKey("toons.id"), nullable=False, index=True
    )
    status = Column(
        Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False
    )
    notes = Column(String(500), nullable=True)
    benched_note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    raid = relationship("Raid", back_populates="attendance")
    toon = relationship("Toon", back_populates="attendance")

    __table_args__ = (
        UniqueConstraint("raid_id", "toon_id", name="uq_attendance_raid_toon"),
        CheckConstraint(
            "notes IS NULL OR TRIM(notes) != ''",
            name="ck_attendance_notes_not_empty",
        ),
        CheckConstraint(
            "benched_note IS NULL OR TRIM(benched_note) != ''",
            name="ck_attendance_benched_note_not_empty",
        ),
    )
