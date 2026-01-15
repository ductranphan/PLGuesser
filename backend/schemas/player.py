from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PlayerBase(BaseModel):
    """Base schema with common player fields"""
    name: str = Field(..., min_length=1, max_length=100)
    nationality: str = Field(..., min_length=1, max_length=100)
    club: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=16, le=50)  # Age between 16 and 50
    goal_contribution: int = Field(..., ge=0, le=100)
    number: int = Field(..., ge=1, le=99)
    height: int = Field(..., ge=150, le=220)  # Height in cm (between 150cm and 220cm)
    photo_url: Optional[str] = Field(None, max_length=500)  # Player photo URL  

class PlayerCreate(PlayerBase):
    """Schema for creating a new player"""
    external_id: Optional[str] = Field(None, max_length=100)


class PlayerResponse(PlayerBase):
    """Schema for API responses (includes id and timestamps)"""
    id: int
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy models
    

