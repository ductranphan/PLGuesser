from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from db.database import Base

class Player(Base):

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    nationality = Column(String(100))
    club = Column(String(100))
    position = Column(String(100))
    age = Column(Integer)
    goal_contribution = Column(Integer)
    number = Column(Integer)
    height = Column(Integer)  # Height in cm
    photo_url = Column(String(500), nullable=True)  # Player photo URL

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
