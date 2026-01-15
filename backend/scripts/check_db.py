"""
Simple script to check database contents
Run this anytime to see what's in your database
"""
import sys
from pathlib import Path

# Add parent directory (backend) to Python path
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from db.database import SessionLocal
from models.player import Player
from models.user import User
from models.user import Game
from sqlalchemy import func

def check_database():
    """Display database contents in a nicely formatted way"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print(" " * 25 + "DATABASE CONTENTS")
        print("=" * 80)
        
        # Count players
        player_count = db.query(Player).count()
        print(f"\n[PLAYERS] {player_count} total")
        
        if player_count > 0:
            # Group by club
            clubs = db.query(Player.club).distinct().order_by(Player.club).all()
            print(f"[CLUBS] {len(clubs)} different clubs")
            
            print("\n" + "=" * 80)
            print("PLAYER LIST (sorted by name)")
            print("=" * 80)
            
            players = db.query(Player).order_by(Player.name).all()
            
            # Display in a table-like format
            print(f"\n{'#':<4} {'Name':<25} {'Club':<20} {'Position':<6} {'Age':<4} {'G/A':<9} {'#':<4} {'Height':<7} {'Nationality':<15}")
            print("-" * 80)
            
            for i, p in enumerate(players, 1):
                name_display = p.name[:24] if len(p.name) <= 24 else p.name[:21] + "..."
                club_display = p.club[:19] if len(p.club) <= 19 else p.club[:16] + "..."
                nationality_display = p.nationality[:14] if len(p.nationality) <= 14 else p.nationality[:11] + "..."
                
                print(f"{i:<4} {name_display:<25} {club_display:<20} {p.position:<6} {p.age:<4} "
                      f"{p.goal_contribution:<9} {p.number:<4} {p.height}cm{'':<2} {nationality_display:<15}")
            
            
            # Count by position
            positions = db.query(Player.position, func.count(Player.id)).group_by(Player.position).all()
            print("\nBy Position:")
            for pos, count in sorted(positions, key=lambda x: -x[1]):
                print(f"  {pos}: {count}")
            
            # Count by club
            club_counts = db.query(Player.club, func.count(Player.id)).group_by(Player.club).order_by(func.count(Player.id).desc()).limit(10).all()
            print("\nTop 10 Clubs by Player Count:")
            for club, count in club_counts:
                print(f"  {club}: {count}")
            
        
        print("\n" + "=" * 80)
        
        # Count users and games
        user_count = db.query(User).count()
        game_count = db.query(Game).count()
        print(f"[USERS] {user_count}  |  [GAMES] {game_count}")

        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()

