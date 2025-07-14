from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    teams = relationship(
        "Team", back_populates="guild", cascade="all, delete-orphan"
    )
    members = relationship(
        "Member", back_populates="guild", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    creator = relationship("User", back_populates="guilds")
