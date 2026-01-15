from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from db.database import get_db
from core.security import get_current_user
from models.user import User, Game
from services.stats import get_user_stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me", response_model=Dict[str, Any])
async def get_my_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = get_user_stats(current_user.id, db)
    return stats

@router.get("/leaderboard")
async def get_leaderboard(Limit: int = 10, db: Session = Depends(get_db)):
    from sqlalchemy import func, case

    leaderboard = db.query(User.id, User.username, func.sum(Game.guesses_used).label("total_guesses")).join(Game).filter(Game.won.is_(True)).group_by(User.id).order_by(func.sum(Game.guesses_used).desc()).limit(Limit).all()

    return [{"username": user.username, "total_guesses": user.total_guesses}
    for user in leaderboard]


