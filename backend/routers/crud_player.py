from fastapi import APIRouter, Depends, HTTPException, status, Query
from db.database import get_db
from models.player import Player
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from core.security import get_current_user
from schemas.player import PlayerResponse
from core.security import get_current_user_optional

# Create router for player endpoints
router = APIRouter(prefix="/players", tags=["players"])

# List/Search players with filters and pagination
@router.get("", response_model=List[PlayerResponse])
async def get_players(
    name: Optional[str] = Query(None, description="Filter by player name (partial match)"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    club: Optional[str] = Query(None, description="Filter by club"),
    position: Optional[str] = Query(None, description="Filter by position"),
    limit: Optional[int] = Query(500, ge=1, le=1000, description="Maximum number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_optional)
):
    """List players with optional filters and pagination (all players in database are Premier League)"""
    query = db.query(Player)
    
    # Apply filters
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))
    if nationality:
        query = query.filter(Player.nationality.ilike(f"%{nationality}%"))
    if club:
        query = query.filter(Player.club.ilike(f"%{club}%"))
    if position:
        query = query.filter(Player.position.ilike(f"%{position}%"))
    
    players = query.offset(offset).limit(limit).all()
    return players

# Search players by name (quick search)
@router.get("/search", response_model=List[PlayerResponse])
async def search_players(
    q: str = Query(..., description="Search query for player name"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_optional)
):
    """Quick search for players by name (for dropdowns/selectors)"""
    print(f"[DEBUG] Searching for: '{q}'")
    
    players = db.query(Player).filter(
        Player.name.ilike(f"%{q}%")
    ).limit(200).all()
    
    print(f"[DEBUG] Found {len(players)} players")
    if players:
        print(f"[DEBUG] First 5 results: {[p.name for p in players[:5]]}")
    
    return players

# Get random player
@router.get("/random", response_model=PlayerResponse)
async def get_random_player(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_optional)
):
    """Get a random player from the database"""
    player = db.query(Player).order_by(func.random()).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No players found in database"
        )
    return player

# Get player by ID (must come last due to route matching)
@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_optional)
):
    """Get player details by ID"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Player not found"
        )
    return player
    

@router.get("/debug/all", response_model=List[PlayerResponse])
async def debug_all_players(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Debug: Get ALL players"""
    players = db.query(Player).all()
    print(f"[DEBUG] Total players in database: {len(players)}")
    return players
