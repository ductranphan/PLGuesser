import sys
from pathlib import Path

# Add backend directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from db.database import SessionLocal
from models.user import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def view_all_users():
    """Display all users in the database"""
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        
        print("\n" + "="*70)
        print(f"📊 TOTAL USERS IN DATABASE: {len(users)}")
        print("="*70 + "\n")
        
        if not users:
            print("⚠️  No users found in the database!")
            return
        
        for idx, user in enumerate(users, 1):
            print(f"User #{idx}")
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Created: {user.created_at}")
            print(f"  Total Games: {user.total_games}")
            print(f"  Games Won: {user.games_won}")
            print(f"  Games Lost: {user.games_lost}")
            print(f"  Current Streak: {user.current_streak}")
            print(f"  Best Streak: {user.best_streak}")
            print("-" * 70)
        
        print(f"\n✅ Successfully displayed {len(users)} users\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    view_all_users()
