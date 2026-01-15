import sys
import argparse
from pathlib import Path

# Add parent directory (backend) to Python path so imports work
# This allows the script to be run from any directory
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from db.database import SessionLocal, create_db_and_tables
from models.player import Player
import models.player  # Import model so SQLAlchemy knows about it
import models.user    # Import model so SQLAlchemy knows about it
from dotenv import load_dotenv
import os
import time
import requests

# Load .env from backend directory (parent of scripts)
load_dotenv(dotenv_path=backend_dir / ".env")

API_TOKEN = os.getenv("soccer_api_key")

# API-Football Configuration (Direct from api-football.com)
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": str(API_TOKEN)  # Direct API-Football uses this header name
}

# Premier League configuration
PREMIER_LEAGUE_API_ID = 39  # API-Football league ID for Premier League
PREMIER_LEAGUE_NAME = "Premier League"  # League name as stored in database

def get_premier_league_teams(season: int = 2024):
    """Get all teams in Premier League"""
    url = f"{BASE_URL}/teams"
    params = {"league": PREMIER_LEAGUE_API_ID, "season": season}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"API Errors: {data['errors']}")
                return []
            
            # API-Football wraps results in response array
            if data.get("response"):
                teams = []
                for team_data in data["response"]:
                    team_info = team_data.get("team", {})
                    teams.append({
                        "id": team_info.get("id"),
                        "name": team_info.get("name", "")
                    })
                return teams
            return []
        else:
            print(f"Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"Failed to fetch teams: {e}")
        return []

def get_team_squad(team_id: int, season: int = 2024):
    """Get squad (all players) for a team using /players/squads endpoint"""
    url = f"{BASE_URL}/players/squads"
    params = {"team": team_id}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"    API Errors: {data['errors']}")
                return []
            
            if data.get("response") and len(data["response"]) > 0:
                squad_data = data["response"][0]
                return squad_data.get("players", [])
            return []
        else:
            print(f"    Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"    Failed to fetch squad: {e}")
        return []

def get_player_statistics(player_id: int, season: int = 2024):
    """Get detailed statistics for a player using /players endpoint"""
    url = f"{BASE_URL}/players"
    params = {"id": player_id, "season": season}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                return None
            
            if data.get("response") and len(data["response"]) > 0:
                return data["response"][0]  # Return first result (contains player + statistics)
            return None
        else:
            return None
    except Exception as e:
        return None

def parse_player_data_from_statistics(statistics_data: dict, player_id_for_squad: int = None, team_id_for_squad: int = None):
    """Parse player data from /players endpoint (for individual player IDs)
    This works when you only have statistics data, not squad data
    If team_id_for_squad is provided, will fetch squad to get accurate number
    """
    if not statistics_data:
        return None
    
    player_info = statistics_data.get("player", {})
    statistics = statistics_data.get("statistics", [])
    
    # Extract player info
    player_id = str(player_info.get("id", ""))
    if not player_id:
        return None
    
    # Get name
    name = player_info.get("name", "")
    
    nationality = player_info.get("nationality", "")
    age = player_info.get("age")
    
    # Get height from player info (usually a string like "179", convert to int)
    height_str = player_info.get("height", "")
    height = None
    if height_str:
        try:
            # Remove "cm" if present and convert to int
            height = int(str(height_str).replace("cm", "").strip())
        except (ValueError, AttributeError):
            height = None
    
    # Get photo URL from player info
    photo_url = player_info.get("photo", "")
    if not photo_url:
        photo_url = None
    
    # Get club, position, number, and goal contribution from Premier League statistics
    club = "Unknown"
    position = "CM"
    number = 0
    goal_contribution = 0
    team_id = None
    
    if statistics and len(statistics) > 0:
        # Filter for Premier League statistics only
        premier_league_stats = []
        for stat in statistics:
            league_info = stat.get("league", {})
            league_id_from_api = league_info.get("id")
            league_name = league_info.get("name", "")
            
            if league_id_from_api == PREMIER_LEAGUE_API_ID or league_name == PREMIER_LEAGUE_NAME:
                premier_league_stats.append(stat)
        
        if premier_league_stats:
            stat = premier_league_stats[0]
            
            # Get team/club name
            team_info = stat.get("team", {})
            club = team_info.get("name", "Unknown")
            team_id = team_info.get("id")
            
            # Get position
            games = stat.get("games", {})
            position_full = games.get("position", "")
            if position_full:
                position = map_position(position_full)
            
            # Note: Number should come from squad data, not statistics
            # Calculate goal contribution
            goals_data = stat.get("goals", {})
            goals = goals_data.get("total", 0) or 0
            assists = goals_data.get("assists", 0) or 0
            goal_contribution = goals + assists
        else:
            # Player doesn't have Premier League statistics
            return None
    
    # Number must come from squad data, not statistics
    # If we have team_id, fetch it from squad
    if (team_id_for_squad or team_id):
        target_team_id = team_id_for_squad or team_id
        target_player_id = player_id_for_squad or int(player_id)
        
        print(f"  Fetching number from squad for team {target_team_id}...")
        squad = get_team_squad(target_team_id)
        time.sleep(6)  # Rate limiting
        
        if squad:
            for squad_player in squad:
                if squad_player.get("id") == target_player_id:
                    squad_number = squad_player.get("number")
                    if squad_number is not None:
                        number = squad_number
                        print(f"  Found number {number} from squad data")
                    else:
                        print(f"  Number not available in squad data, defaulting to 0")
                    break
        else:
            print(f"  Warning: Could not fetch squad data, number will be 0")
    else:
        print(f"  Warning: No team_id available, cannot fetch number from squad")
    
    player_data = {
        "external_id": player_id,
        "name": name,
        "nationality": nationality,
        "club": club,
        "position": position,
        "age": age or 25,
        "goal_contribution": goal_contribution,
        "number": number,
        "height": height or 175,  # Default to 175cm if not available
        "photo_url": photo_url,
    }
    
    return player_data

def test_api_connection():
    """Test if API connection is working"""
    print("Testing API connection...")
    # API-Football doesn't have a status endpoint, test with a simple call
    url = f"{BASE_URL}/status"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status endpoint response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "errors" in data and data["errors"]:
                print(f"API Errors: {data['errors']}")
                return False
            print(f"API Status: {data.get('response', 'OK')}")
            return True
        else:
            print(f"API Status check failed: {response.text}")
            return False
    except Exception as e:
        print(f"API connection test failed: {e}")
        return False


def parse_squad_player(squad_player: dict, team_name: str):
    """Parse basic player info from squad endpoint
    Returns: player_id, name, age, number, position (basic info only)
    """
    if not squad_player:
        return None
    
    player_id = str(squad_player.get("id", ""))
    if not player_id:
        return None
    
    # Get name - use name field if available, otherwise combine firstname + lastname
    name = squad_player.get("name", "")
    
    age = squad_player.get("age")
    # Get number directly from squad player (can be None or 0)
    number = squad_player.get("number")
    if number is None:
        number = 0
    position_full = squad_player.get("position", "")
    position = map_position(position_full)
    
    # Get photo URL from squad player
    photo_url = squad_player.get("photo", "")
    if not photo_url:
        photo_url = None
    
    return {
        "external_id": player_id,
        "name": name,
        "age": age,
        "number": number,
        "position": position,
        "photo_url": photo_url,
        "team_name": team_name,  # Temporary, will be replaced by club from stats
    }

def seed_single_player(player_id: int, season: int = 2024):
    """Seed a single player by ID (for testing or adding specific players)
    Returns True if successful, False otherwise
    """
    db = SessionLocal()
    try:
        player_id_str = str(player_id)
        
        # Check if player already exists
        existing = db.query(Player).filter(
            Player.external_id == player_id_str
        ).first()
        
        if existing:
            print(f"Player {player_id} ({existing.name}) already exists in database")
            return True
        
        # Get player statistics
        print(f"Fetching player ID {player_id}...")
        stats_data = get_player_statistics(player_id, season=season)
        time.sleep(6)  # Rate limiting
        
        if not stats_data:
            print(f"Failed to fetch player data for ID {player_id}")
            return False
        
        # Extract team_id from statistics before parsing (needed for squad lookup)
        team_id = None
        if stats_data.get("statistics"):
            for stat in stats_data["statistics"]:
                league_info = stat.get("league", {})
                if league_info.get("id") == PREMIER_LEAGUE_API_ID:
                    team_info = stat.get("team", {})
                    team_id = team_info.get("id")
                    break
        
        # Parse player data from statistics (will fetch squad if needed for number)
        player_data = parse_player_data_from_statistics(stats_data, player_id_for_squad=player_id, team_id_for_squad=team_id)
        
        if not player_data:
            print(f"Player {player_id} does not have Premier League statistics")
            return False
        
        # Create and add player
        player = Player(**player_data)
        db.add(player)
        db.commit()
        
        print(f"[OK] Added: {player_data['name']} ({player_data['club']})")
        print(f"  Position: {player_data['position']}, Age: {player_data['age']}")
        print(f"  Goal Contribution: {player_data['goal_contribution']}, Number: {player_data['number']}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        return False
    finally:
        db.close()

def parse_player_statistics(statistics_data: dict, basic_info: dict):
    """Parse detailed statistics and combine with basic info from squad
    Returns complete player data for database
    """
    if not statistics_data or not basic_info:
        return None
    
    statistics = statistics_data.get("statistics", [])
    player_info = statistics_data.get("player", {})
    
    # Get nationality from player info
    nationality = player_info.get("nationality", "")
    
    # Get height from player info (usually a string like "179", convert to int)
    height_str = player_info.get("height", "")
    height = None
    if height_str:
        try:
            # Remove "cm" if present and convert to int
            height = int(str(height_str).replace("cm", "").strip())
        except (ValueError, AttributeError):
            height = None
    
    # Get photo URL from player info (prefer from stats, fallback to squad if available)
    photo_url = player_info.get("photo", "")
    if not photo_url:
        photo_url = basic_info.get("photo_url", None)
    if not photo_url:
        photo_url = None
    
    # Get club, position, number, and goal contribution from Premier League statistics
    club = basic_info.get("team_name", "Unknown")
    position = basic_info.get("position", "CM")
    number = basic_info.get("number", 0)
    goal_contribution = 0
    
    if statistics and len(statistics) > 0:
        # Filter for Premier League statistics only
        premier_league_stats = []
        for stat in statistics:
            league_info = stat.get("league", {})
            league_id_from_api = league_info.get("id")
            league_name = league_info.get("name", "")
            
            # Check if this is Premier League (ID 39 or name matches)
            if league_id_from_api == PREMIER_LEAGUE_API_ID or league_name == PREMIER_LEAGUE_NAME:
                premier_league_stats.append(stat)
        
        # If we found Premier League statistics, use the first one
        if premier_league_stats:
            stat = premier_league_stats[0]
            
            # Get team/club name (prefer from stats as it's more accurate)
            team_info = stat.get("team", {})
            club = team_info.get("name", club)
            
            # Get position from games.position (override if available in stats)
            games = stat.get("games", {})
            position_full = games.get("position", "")
            if position_full:
                position = map_position(position_full)
            
            # Note: Number should only come from squad data (already in basic_info), not from statistics
            
            # Calculate goal contribution: goals + assists
            goals_data = stat.get("goals", {})
            goals = goals_data.get("total", 0) or 0
            assists = goals_data.get("assists", 0) or 0
            goal_contribution = goals + assists
        else:
            # Player has no Premier League statistics - skip them
            return None
    
    # Combine basic info from squad with detailed stats
    player_data = {
        "external_id": basic_info.get("external_id"),
        "name": basic_info.get("name", ""),
        "nationality": nationality,
        "club": club or "Unknown",
        "position": position,
        "age": basic_info.get("age") or 25,
        "goal_contribution": goal_contribution,
        "number": number,
        "height": height or 175,  # Default to 175cm if not available
        "photo_url": photo_url,
    }
    
    return player_data

def map_position(position: str):
    """Map API-Football position string to position code.
    API only returns: Goalkeeper, Defender, Midfielder, Attacker
    """
    if not position:
        return "CM"  # Default if no position
    
    position = position.strip()
    
    # Simple mapping for the 4 positions API-Football returns
    position_map = {
        "Goalkeeper": "GK",
        "Defender": "CB",
        "Midfielder": "CM",
        "Attacker": "ST",
    }
    
    # Try exact match (case-sensitive first)
    if position in position_map:
        return position_map[position]
    
    # Try case-insensitive match
    position_lower = position.lower()
    for key, code in position_map.items():
        if key.lower() == position_lower:
            return code
    
    # Unknown position - default to CM
    print(f"  [Warning] Unknown position '{position}', defaulting to 'CM'")
    return "CM"

def seed_database():
    """Main function to seed the database using efficient squad-based approach"""
    # ADD THIS BLOCK AT THE VERY TOP:
    from db.database import engine
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    print(f"[DEBUG] Script location: {script_dir}")
    print(f"[DEBUG] Backend directory: {backend_dir}")
    print(f"[DEBUG] Database URL: {engine.url}")
    print(f"[DEBUG] Resolved database path: {engine.url.database}")
    print()
    
    # Create database tables if they don't exist
    print("Creating database tables...")
    create_db_and_tables()
    print("[OK] Database tables ready")
    
    # Test API connection first
    print("\nTesting API connection...")
    if not API_TOKEN:
        print("[ERROR] API_TOKEN not found in environment variables!")
        print("   Make sure you have 'soccer_api_key' in your .env file")
        return
    
    print(f"API Token found: {API_TOKEN[:10]}..." if len(API_TOKEN) > 10 else "API Token found")
    if not test_api_connection():
        print("\n[Warning] API connection test failed, but continuing anyway...")
    
    print()
    db = SessionLocal()

    try:
        # Step 1: Get all Premier League teams
        print("Step 1: Fetching Premier League teams...")
        teams = get_premier_league_teams(season=2024)
        
        if not teams:
            print("[ERROR] Failed to fetch Premier League teams")
            return
        
        print(f"[OK] Found {len(teams)} teams in Premier League")
        time.sleep(6)  # Rate limiting
        
        total_players_added = 0
        total_players_skipped = 0
        
        # Pre-load all existing player external_ids into a set for fast lookup
        print("Loading existing players from database...")
        existing_players = set()
        existing_db_players = db.query(Player.external_id).all()
        for (external_id,) in existing_db_players:
            existing_players.add(str(external_id))
        print(f"[OK] Found {len(existing_players)} existing players in database")
        
        # Pre-load all existing clubs/teams that already have players (for info only)
        print("Loading existing teams from database...")
        existing_clubs = set()
        existing_db_clubs = db.query(Player.club).distinct().all()
        for (club,) in existing_db_clubs:
            if club:
                existing_clubs.add(club.strip())
        print(f"[OK] Found {len(existing_clubs)} teams already in database: {', '.join(sorted(existing_clubs))}")
        
        # Teams that are considered "full" and should be skipped entirely
        full_teams = {
            "newcastle",
            "manu",
            "wolves",
            "liverpool",
            "leicester",
            "southampton",
            "fullham",
            "everton",
            "bournemout",
            "westham",
        }
        
        def normalize_team_name(name: str) -> str:
            return "".join(ch for ch in name.lower().strip() if ch.isalnum())
        
        total_teams_skipped = 0
        
        # Step 2: For each team, get squad and then detailed stats for each player
        try:
            for team_idx, team in enumerate(teams, 1):
                team_id = team["id"]
                team_name = team["name"]
                
                # Skip only teams that are known to be "full"
                if normalize_team_name(team_name) in full_teams:
                    print(f"\n[{team_idx}/{len(teams)}] [SKIP TEAM] {team_name} is marked as full - skipping entire team")
                    total_teams_skipped += 1
                    continue
                
                print(f"\n[{team_idx}/{len(teams)}] Processing {team_name} (Team ID: {team_id})...")
                
                # Get squad (all players in team)
                squad = get_team_squad(team_id, season=2024)
                time.sleep(6)  # Rate limiting after squad request
                
                if not squad:
                    print(f"  [Warning] No squad data found for {team_name}")
                    continue
                
                print(f"  Found {len(squad)} players in squad")
                
                # Filter out players that already exist before processing
                new_players = []
                for squad_player in squad:
                    player_id = squad_player.get("id")
                    if not player_id:
                        continue
                    player_id_str = str(player_id)
                    if player_id_str not in existing_players:
                        new_players.append(squad_player)
                    else:
                        total_players_skipped += 1
                
                if not new_players:
                    print(f"  [SKIP] All {len(squad)} players from {team_name} already exist in database")
                    continue
                
                print(f"  Processing {len(new_players)} new players (skipped {len(squad) - len(new_players)} existing)")
                
                # Process each new player in the squad
                for player_idx, squad_player in enumerate(new_players, 1):
                    player_id = squad_player.get("id")
                    if not player_id:
                        continue
                    
                    player_id_str = str(player_id)
                    
                    # Parse basic info from squad
                    basic_info = parse_squad_player(squad_player, team_name)
                    if not basic_info:
                        continue
                    
                    # Get detailed statistics for this player
                    stats_data = get_player_statistics(player_id, season=2024)
                    time.sleep(6)  # Rate limiting after stats request
                    
                    if not stats_data:
                        print(f"    [{player_idx}/{len(new_players)}] [Warning] No statistics found for {basic_info['name']}")
                        continue
                    
                    # Combine basic info with detailed stats
                    player_data = parse_player_statistics(stats_data, basic_info)
                    
                    if not player_data:
                        # Player doesn't have Premier League statistics (might be on loan, etc.)
                        continue
                    
                    # Create and add player to database
                    player = Player(**player_data)
                    db.add(player)
                    total_players_added += 1
                    
                    # Add to our set so we don't fetch it again in this run
                    existing_players.add(player_id_str)
                    
                    # Commit after each player to save progress (safe to interrupt)
                    db.commit()
                    
                    print(f"    [{player_idx}/{len(new_players)}] Added: {player_data['name']} ({player_data['club']})")
                    print(f"      Position: {player_data['position']}, Age: {player_data['age']}, Nationality: {player_data['nationality']}")
                    print(f"      Goal Contribution: {player_data['goal_contribution']}, Number: {player_data['number']}")
            
            # Final summary
            print(f"\n[OK] Database seeded successfully!")
            print(f"  Total players added: {total_players_added}")
            print(f"  Total players skipped (already existed): {total_players_skipped}")
            
        except KeyboardInterrupt:
            # User pressed Ctrl+C - save progress and exit gracefully
            print(f"\n\n[INTERRUPTED] Seeding stopped by user (Ctrl+C)")
            print(f"  Committing progress so far...")
            db.commit()
            print(f"  Progress saved!")
            print(f"  Total teams skipped: {total_teams_skipped}")
            print(f"  Total players added before interruption: {total_players_added}")
            print(f"  Total players skipped: {total_players_skipped}")
            print(f"  You can resume by running the script again - it will skip full teams and existing players")
            raise  # Re-raise to exit
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Database session closed")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Premier League players database")
    parser.add_argument(
        "--player-id", 
        type=int, 
        help="Seed a single player by ID (e.g., --player-id 1485)"
    )
    parser.add_argument(
        "--season",
        type=int,
        default=2024,
        help="Season year (default: 2024)"
    )
    
    args = parser.parse_args()
    
    if args.player_id:
        # Seed a single player
        print(f"Seeding single player: ID {args.player_id}")
        create_db_and_tables()  # Ensure tables exist
        seed_single_player(args.player_id, season=args.season)
    else:
        # Seed all players (bulk)
        seed_database()

    




