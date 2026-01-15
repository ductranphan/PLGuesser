from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.user import Game
from datetime import datetime

def get_user_stats(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Calculate user statistics from their game history
    """
    # Get all completed games for this user
    # Filter by games that are either won or lost (completed)
    # Use won.isnot(None) to ensure game is completed (won=True or won=False)
    completed_games = db.query(Game).filter(
        and_(
            Game.user_id == user_id,
            Game.won.isnot(None)  # Game is completed (won=True or won=False)
        )
    ).order_by(Game.completed_at.desc()).all()
    
    # Sort to handle NULL completed_at values (put them at the end)
    completed_games = sorted(
        completed_games, 
        key=lambda g: g.completed_at if g.completed_at else datetime.min,
        reverse=True
    )
    
    if not completed_games:
        return {
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "win_rate": 0.0,
            "current_streak": 0,
            "best_streak": 0,
            "average_guesses": 0.0,
            "guess_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
            "perfect_games": 0,
            "clutch_wins": 0,
            "first_guess_wins": 0
        }

    games_played = len(completed_games)
    games_won = sum(1 for game in completed_games if game.won)
    games_lost = games_played - games_won
    win_rate = games_won / games_played if games_played > 0 else 0.0
    

    current_streak = 0
    best_streak = 0
    temp_streak = 0

    for game in reversed(completed_games):
        if game.won:
            if current_streak == temp_streak:
                current_streak += 1
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            if current_streak == temp_streak:
                current_streak = 0
            temp_streak = 0

    won_games = [game for game in completed_games if game.won]
    average_guesses = sum(game.guesses_used for game in won_games) / len(won_games) if won_games else 0.0

    guess_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for game in won_games:
        if 1 <= game.guesses_used <= 6:
            guess_distribution[game.guesses_used] += 1

    perfect_games = sum(1 for game in won_games if game.guesses_used == 1)
    clutch_wins = sum(1 for game in won_games if game.guesses_used == 1 and game.won)
    first_guess_wins = sum(1 for game in won_games if game.guesses_used == 1 and game.won)

    return {
        "games_played": games_played,
        "games_won": games_won,
        "games_lost": games_lost,
        "win_rate": win_rate,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "average_guesses": average_guesses,
        "guess_distribution": guess_distribution,
        "perfect_games": perfect_games,
        "clutch_wins": clutch_wins,
        "first_guess_wins": first_guess_wins
    }

