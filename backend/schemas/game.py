from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from schemas.player import PlayerResponse


class GameBase(BaseModel):
    """Base schema with common game fields"""
    game_status: str = Field(default="pending", max_length=50)  # pending, in_progress, won, lost
    game_result: str = Field(default="pending", max_length=50)  # pending, won, lost
    game_score: int = Field(default=0, ge=0)  # Number of guesses used (0-6)


class GameCreate(BaseModel):
    """Schema for creating a new game (starts a new Wordle game)"""
    # When creating, we'll select a random secret player
    # game_data will be initialized with the secret player ID
    pass


class GuessResult(BaseModel):
    """Schema for a single guess result (comparison hints)"""
    guessed_player_id: int
    guessed_player: PlayerResponse  # The player they guessed
    hints: Dict[str, Any] = Field(
        ...,
        description="Comparison hints: name, nationality, club, position, age, goal_contribution, number (each with 'value' and 'result': 'correct', 'close', or 'incorrect')"
    )


class GameResponse(GameBase):
    """Schema for API responses"""
    id: int
    user_id: Optional[int]
    game_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Contains: secret_player_id, guesses (list of GuessResult)"
    )
    guesses: Optional[List[GuessResult]] = Field(
        None,
        description="List of guesses made in this game"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GameGuess(BaseModel):
    """Schema for submitting a guess"""
    player_id: int = Field(..., description="ID of the player being guessed")


class GameGuessResponse(BaseModel):
    """Schema for guess submission response"""
    guess_result: GuessResult
    game_status: str  # Updated game status after guess
    game_result: str  # Updated game result
    is_correct: bool  # Whether the guess was correct
    guesses_remaining: int  # Number of guesses left (0-6)
