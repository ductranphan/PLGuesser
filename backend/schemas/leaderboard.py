from pydantic import BaseModel
from typing import Optional

class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    total_wins: int
    total_games_played: int
    win_percentage: float
    current_win_streak: int
    best_win_streak: int
    average_guesses: float
    rank: int

    class Config:
        from_attributes = True

class UserStats(BaseModel):
    total_games_played: int
    total_wins: int
    total_losses: int
    win_percentage: float
    current_win_streak: int
    best_win_streak: int
    average_guesses: Optional[float] = None
    
    class Config:
        from_attributes = True