from fastapi import APIRouter, Depends, HTTPException, status, Query
from schemas.game import GameCreate, GameResponse, GameGuess, GuessResult
from db.database import get_db
from services.game_logic import is_correct_guess, compare_players    
from models.player import Player
from models.user import User, Game
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
from typing import List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from core.security import get_current_user, get_current_user_optional
from core.config import MAX_GUESSES
from schemas.player import PlayerResponse

router = APIRouter(prefix="/games", tags=["games"])

def get_eastern_tz():
    try:
        return ZoneInfo("America/New_York")
    except ZoneInfoNotFoundError:
        # Fallback to UTC if tzdata is missing; install tzdata for ET
        print("[WARN] tzdata not found. Falling back to UTC. Install tzdata for ET.")
        return ZoneInfo("UTC")

def update_user_stats(db: Session, user: User, game: Game):
    """Update user statistics after a game ends (only for daily challenges)"""
    # Increment games played
    user.total_games_played += 1
    
    if game.game_result == "won":
        # Increment wins
        user.total_wins += 1
        
        # Update win streak
        user.current_win_streak += 1
        if user.current_win_streak > user.best_win_streak:
            user.best_win_streak = user.current_win_streak
        
        # Update average guesses (for won games only)
        total_guesses_sum = (user.average_guesses * (user.total_wins - 1)) + game.game_score
        user.average_guesses = total_guesses_sum / user.total_wins
        
    elif game.game_result == "lost":
        # Increment losses
        user.total_losses += 1
        
        # Reset win streak
        user.current_win_streak = 0
    
    db.commit()

def get_existing_daily_challenge(db: Session, user_id: int) -> Optional[Game]:
    """Return today's daily challenge game for user if it exists."""
    tz = get_eastern_tz()
    today = datetime.now(tz).date()
    start_of_day = datetime(today.year, today.month, today.day, tzinfo=tz)
    end_of_day = start_of_day + timedelta(days=1)

    games_today = db.query(Game).filter(
        Game.user_id == user_id,
        Game.created_at >= start_of_day,
        Game.created_at < end_of_day
    ).all()

    for game in games_today:
        if game.game_data and game.game_data.get("is_daily_challenge"):
            return game
    return None

def build_game_response(game: Game, guesses: Optional[list] = None) -> GameResponse:
    return GameResponse(
        id=game.id,
        user_id=game.user_id,
        game_status=game.game_status,
        game_result=game.game_result,
        game_score=game.game_score,
        game_data=game.game_data,
        guesses=guesses or [],
        created_at=game.created_at,
        updated_at=game.updated_at,
    )

#THIS FUNCTION TAKES THE GUYS WITH THE MOST CONTRIBUTIONS TO GUESS, ILL CHANGE LATER TO A MORE ACCURATE METHOD
def select_popular_player(db: Session, limit: int = 20) -> Optional[Player]:
    """Select a popular player based on goal contribution, with fallback."""
    popular_players = (
        db.query(Player)
        .filter(Player.goal_contribution.isnot(None))
        .order_by(Player.goal_contribution.desc(), Player.id.asc())
        .limit(limit)
        .all()
    )
    if not popular_players:
        return db.query(Player).order_by(func.random()).first()
    return random.choice(popular_players)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////

def select_daily_challenge_player(db: Session, limit: int = 20) -> Optional[Player]:
    """Pick a deterministic 'player of the day' from popular players."""
    base_query = (
        db.query(Player)
        .filter(Player.goal_contribution.isnot(None))
        .order_by(Player.goal_contribution.desc(), Player.id.asc())
    )
    total = base_query.count()
    if total == 0:
        return db.query(Player).order_by(func.random()).first()

    pool_size = min(total, limit)
    tz = get_eastern_tz()
    index = datetime.now(tz).date().toordinal() % pool_size
    return base_query.limit(pool_size).offset(index).first()
#///////////////////////////////////////////////////////////////////////////////////////////

# DAILY CHALLENGE - Requires login
@router.post("", response_model=GameResponse)
async def create_daily_challenge_game(
    game: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or return today's daily challenge for logged-in user."""
    existing = get_existing_daily_challenge(db, current_user.id)
    if existing:
        guesses = existing.game_data.get("guesses", []) if existing.game_data else []
        return build_game_response(existing, guesses)

    secret_player = select_daily_challenge_player(db)
    if not secret_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No players found in database. Please seed the database first."
        )

    new_game = Game(
        user_id=current_user.id,
        game_status="in_progress",
        game_result="pending",
        game_score=0,
        won=None,
        guesses_used=0,
        completed_at=None,
        game_data={
            "secret_player_id": secret_player.id,
            "guesses": [],
            "game_mode": "daily_challenge",
            "is_daily_challenge": True,
            "challenge_date": datetime.now(get_eastern_tz()).date().isoformat(),
        }
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return build_game_response(new_game, [])

# FREE PLAY MODE - No authentication required
@router.post("/free-play", response_model=GameResponse)
async def create_free_play_game(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a free play game (no login required, unlimited games, no stats tracking)"""
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free play is only available for guests. Log out to play free play."
        )
    # Select a random player as the secret/target player
    secret_player = select_popular_player(db)
    
    if not secret_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No players found in database. Please seed the database first."
        )
    
    # Initialize game with no user (anonymous)
    new_game = Game(
        user_id=None,  # No user for free play
        game_status="in_progress",
        game_result="pending",
        game_score=0,
        won=None,
        guesses_used=0,
        completed_at=None,
        game_data={
            "secret_player_id": secret_player.id,
            "guesses": [],
            "game_mode": "free_play",
            "is_daily_challenge": False
        }
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    
    return build_game_response(new_game, [])


# Submit a guess (works for both free play and daily challenge)
@router.post("/{game_id}/guess", response_model=GameResponse)
async def submit_guess(
    game_id: int, 
    guess_data: GameGuess, 
    db: Session = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Submit a guess for a game (works for free play, practice, and daily challenge)"""
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        
        # Check ownership
        # Allow if: game is anonymous (user_id is None) OR user owns the game
        if game.user_id is not None:
            if not current_user or game.user_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        else:
            # If logged in, block playing guest free-play games
            if current_user and game.game_data and game.game_data.get("game_mode") == "free_play":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Free play is only available for guests. Log out to continue this game."
                )
        
        if game.game_status not in ["pending", "in_progress"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Game is already {game.game_status}"
            )
        
        # Get the guessed player
        guessed_player = db.query(Player).filter(
            Player.id == guess_data.player_id
        ).first()
        
        if not guessed_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Player not found"
            )
        
        # Get the secret/target player
        secret_player_id = game.game_data.get("secret_player_id") if game.game_data else None
        if not secret_player_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Game data corrupted: no secret player found"
            )
        
        secret_player = db.query(Player).filter(Player.id == secret_player_id).first()
        if not secret_player:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Secret player not found in database"
            )
        
        # Compare players to get hints
        hints = compare_players(guessed_player, secret_player)
        
        # Check if guess is correct
        is_correct = is_correct_guess(guessed_player, secret_player)
        
        # Get existing guesses and make a copy
        existing_guesses = game.game_data.get("guesses", []) if game.game_data else []
        guesses = list(existing_guesses)
        
        # Create new guess result - build as dict
        new_guess = {
            "guessed_player_id": guessed_player.id,
            "guessed_player": {
                "id": guessed_player.id,
                "name": getattr(guessed_player, 'name', None),
                "club": getattr(guessed_player, 'club', None),
                "nationality": getattr(guessed_player, 'nationality', None),
                "position": getattr(guessed_player, 'position', None),
                "age": getattr(guessed_player, 'age', None),
                "number": getattr(guessed_player, 'number', None),
                "goal_contribution": getattr(guessed_player, 'goal_contribution', None),
                "height": getattr(guessed_player, 'height', None),
                "photo_url": getattr(guessed_player, 'photo_url', None),
            },
            "hints": hints
        }
        
        # Add guess to list
        guesses.append(new_guess)
        
        # Preserve game mode and daily challenge info
        game_mode = game.game_data.get("game_mode", "free_play")
        is_daily_challenge = game.game_data.get("is_daily_challenge", False)
        challenge_id = game.game_data.get("challenge_id")
        
        # Update game data
        game.game_data = {
            "secret_player_id": secret_player_id,
            "guesses": guesses,
            "game_mode": game_mode,
            "is_daily_challenge": is_daily_challenge,
            "challenge_id": challenge_id
        }
        
        # Update game score (number of guesses used)
        game.game_score = len(guesses)
        game.guesses_used = len(guesses)
        
        # Update game status
        if is_correct:
            game.game_status = "won"
            game.game_result = "won"
            game.won = True
            game.completed_at = datetime.utcnow()
            
            # Update stats ONLY for daily challenges, not free play or practice
            if current_user and is_daily_challenge:
                update_user_stats(db, current_user, game)
            
        elif len(guesses) >= MAX_GUESSES:
            game.game_status = "lost"
            game.game_result = "lost"
            game.won = False
            game.completed_at = datetime.utcnow()
            
            # Update stats ONLY for daily challenges, not free play or practice
            if current_user and is_daily_challenge:
                update_user_stats(db, current_user, game)
            
        else:
            game.game_status = "in_progress"
            game.won = None
        
        # Commit changes
        db.commit()
        db.refresh(game)
        
        # Build response with the guesses we just created
        response = GameResponse(
            id=game.id,
            user_id=game.user_id,
            game_status=game.game_status,
            game_result=game.game_result,
            game_score=game.game_score,
            game_data=game.game_data,
            guesses=guesses,
            created_at=game.created_at,
            updated_at=game.updated_at,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in submit_guess: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Get the full game state
@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get full game state (works for free play and logged-in users)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    
    if game.user_id is not None:
        if not current_user or game.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Get guesses from game_data
    guesses_list = []
    if game.game_data and game.game_data.get("guesses"):
        guesses_list = game.game_data.get("guesses", [])
    
    return GameResponse(
        id=game.id,
        user_id=game.user_id,
        game_status=game.game_status,
        game_result=game.game_result,
        game_score=game.game_score,
        game_data=game.game_data,
        guesses=guesses_list,
        created_at=game.created_at,
        updated_at=game.updated_at,
    )

# List all games for authenticated user
@router.get("", response_model=List[GameResponse])
async def list_games(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by game status"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """List all games for the current user"""
    query = db.query(Game).filter(Game.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Game.game_status == status_filter)
    
    games = query.order_by(Game.created_at.desc()).all()
    return games