from sqlalchemy import Column, Integer, String, DateTime, Boolean,Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    games = relationship("Game", back_populates="user")
    total_games_played = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    current_win_streak = Column(Integer, default=0)
    best_win_streak = Column(Integer, default=0)
    average_guesses = Column(Float, default=0.0)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="games")

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    
    season = Column(String, default="2024")
    game_data = Column(JSON)

    # Game status can be:
    game_status = Column(String, default="pending")
    won = Column(Boolean, nullable=True) # True if won, False if lost, None if in progress
    guesses_used = Column(Integer, default=0)

    game_result = Column(String, default="pending")
    game_score = Column(Integer, default=0)