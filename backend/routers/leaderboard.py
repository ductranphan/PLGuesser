from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, case
from typing import List
from db.database import get_db
from models.user import User
from core.security import get_current_user
from schemas.leaderboard import LeaderboardEntry, UserStats

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/global", response_model=List[LeaderboardEntry])
async def get_global_leaderboard(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get global leaderboard sorted by total wins first, then win rate"""
    
    # Only include users who have played at least 1 game
    query = db.query(User).filter(User.total_games_played > 0)
    
    # Sort by total wins first (most important), then win rate, then average guesses (lower is better)
    query = query.order_by(
        desc(User.total_wins),  # Primary: Most wins ranks highest
        desc(
            case(
                (User.total_games_played > 0, User.total_wins * 100.0 / User.total_games_played),
                else_=0
            )
        ),  # Secondary: Win rate as tiebreaker
        case((User.average_guesses.is_(None), 1), else_=0),
        User.average_guesses  # Tertiary: Lower average guesses is better
    )
    
    users = query.limit(limit).all()
    
    # Build leaderboard entries with ranks
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        win_percentage = (user.total_wins / user.total_games_played * 100) if user.total_games_played > 0 else 0
        
        entry = LeaderboardEntry(
            user_id=user.id,
            username=user.username,
            total_wins=user.total_wins,
            total_games_played=user.total_games_played,
            win_percentage=round(win_percentage, 1),
            current_win_streak=user.current_win_streak,
            best_win_streak=user.best_win_streak,
            average_guesses=round(user.average_guesses, 2) if user.average_guesses else 0,
            rank=rank
        )
        leaderboard.append(entry)
    
    return leaderboard

@router.get("/me", response_model=UserStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics"""
    # Refresh user from DB to get latest stats
    db.refresh(current_user)
    
    win_percentage = (current_user.total_wins / current_user.total_games_played * 100) if current_user.total_games_played > 0 else 0
    
    return UserStats(
        total_games_played=current_user.total_games_played,
        total_wins=current_user.total_wins,
        total_losses=current_user.total_losses,
        win_percentage=round(win_percentage, 1),
        current_win_streak=current_user.current_win_streak,
        best_win_streak=current_user.best_win_streak,
        average_guesses=round(current_user.average_guesses, 2) if current_user.average_guesses else None
    )

@router.get("/my-rank")
async def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's rank on the leaderboard"""
    
    # Only include users who have played at least 1 game
    query = db.query(User).filter(User.total_games_played > 0)
    
    # Sort by total wins first (most important), then win rate, then average guesses (lower is better)
    query = query.order_by(
        desc(User.total_wins),  # Primary: Most wins ranks highest
        desc(
            case(
                (User.total_games_played > 0, User.total_wins * 100.0 / User.total_games_played),
                else_=0
            )
        ),  # Secondary: Win rate as tiebreaker
        case((User.average_guesses.is_(None), 1), else_=0),
        User.average_guesses  # Tertiary: Lower average guesses is better
    )
    
    users = query.all()
    
    # Find user's rank
    rank = None
    for idx, user in enumerate(users, start=1):
        if user.id == current_user.id:
            rank = idx
            break
    
    total_players = len(users)
    
    return {
        "rank": rank,
        "total_players": total_players
    }