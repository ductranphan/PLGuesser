from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base schema with common user fields (NO PASSWORD!)"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user (registration)"""
    password: str = Field(..., min_length=8, max_length=72, description="Password (bcrypt has 72-byte limit)")

class UserResponse(UserBase):
    """Schema for API responses (NEVER includes password!)"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password (bcrypt has 72-byte limit)")
