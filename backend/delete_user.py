"""
Script to view and delete users from the database
"""
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

def display_all_users(db):
    """Display all users in the database"""
    users = db.query(User).all()
    
    if not users:
        print("⚠️  No users found in the database!")
        return []
    
    print("\n" + "="*80)
    print(f"📊 ALL USERS IN DATABASE ({len(users)} total)")
    print("="*80 + "\n")
    
    for user in users:
        print(f"ID: {user.id} | Username: {user.username} | Email: {user.email}")
        print(f"   Created: {user.created_at} | Games: {user.total_games_played} | Wins: {user.total_wins}")
        print("-" * 80)
    
    return users

def delete_user_by_id(user_id: int):
    """Delete a user by their ID"""
    db = SessionLocal()
    try:
        # Display all users first
        users = display_all_users(db)
        
        if not users:
            return
        
        # Check if user exists
        user_to_delete = db.query(User).filter(User.id == user_id).first()
        
        if not user_to_delete:
            print(f"\n❌ User with ID {user_id} not found!")
            return
        
        # Show user details
        print(f"\n⚠️  You are about to delete:")
        print(f"   ID: {user_to_delete.id}")
        print(f"   Username: {user_to_delete.username}")
        print(f"   Email: {user_to_delete.email}")
        print(f"   Total Games: {user_to_delete.total_games_played}")
        
        # Confirm deletion
        confirmation = input(f"\n⚠️  Type 'DELETE' to confirm deletion of user '{user_to_delete.username}': ")
        
        if confirmation != "DELETE":
            print("\n❌ Deletion cancelled.")
            return
        
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
        
        print(f"\n✅ Successfully deleted user '{user_to_delete.username}' (ID: {user_id})")
        
        # Show remaining users
        print("\n📊 Remaining users:")
        display_all_users(db)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error deleting user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def delete_user_interactive():
    """Interactive mode - list users and ask which to delete"""
    db = SessionLocal()
    try:
        # Display all users
        users = display_all_users(db)
        
        if not users:
            return
        
        # Ask which user to delete
        print("\n" + "="*80)
        user_input = input("Enter the ID of the user you want to delete (or 'q' to quit): ")
        
        if user_input.lower() == 'q':
            print("\n❌ Cancelled.")
            return
        
        try:
            user_id = int(user_input)
        except ValueError:
            print("\n❌ Invalid ID. Please enter a number.")
            return
        
        db.close()  # Close this session before calling delete function
        
        # Delete the user
        delete_user_by_id(user_id)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    print("\n🗑️  USER DELETION TOOL")
    print("="*80)
    
    # Check if user ID was provided as argument
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
            delete_user_by_id(user_id)
        except ValueError:
            print("❌ Invalid user ID. Please provide a numeric ID.")
    else:
        # Interactive mode
        delete_user_interactive()
