import pandas as pd
import os
from pathlib import Path
from .config import DATA_PATHS

# Define paths to EXISTING data (ReadOnly)
EXISTING_DATA_DIR = Path("data/processed")
OL_MATCHES_PATH = EXISTING_DATA_DIR / "ol_match_score_final.csv"
OL_ABSENCES_PATH = EXISTING_DATA_DIR / "ol_absence_impact.csv"
LIGUE1_STANDINGS_PATH = EXISTING_DATA_DIR / "league1_standings_home_away.csv"

def load_existing_data():
    """
    Loads data from the existing project structure without modifying it.
    Returns a dictionary of DataFrames.
    """
    data = {}
    
    # Load OL Matches
    if OL_MATCHES_PATH.exists():
        data['ol_matches'] = pd.read_csv(OL_MATCHES_PATH)
    else:
        print(f"WARNING: Could not find {OL_MATCHES_PATH}")
        data['ol_matches'] = pd.DataFrame()

    # Load Absences
    if OL_ABSENCES_PATH.exists():
        data['absences'] = pd.read_csv(OL_ABSENCES_PATH)
    else:
        data['absences'] = pd.DataFrame()

    # Load Standings
    if LIGUE1_STANDINGS_PATH.exists():
        data['standings'] = pd.read_csv(LIGUE1_STANDINGS_PATH)
    else:
        data['standings'] = pd.DataFrame()
        
    return data

def initialize_new_datasets():
    """
    Creates the new CSV structure for the prediction engine if it doesn't exist.
    """
    # Create prediction_engine/data if not exists
    os.makedirs(os.path.dirname(DATA_PATHS['matches_db']), exist_ok=True)
    
    # Manager H2H Template
    if not os.path.exists(DATA_PATHS['manager_h2h']):
        df_manager = pd.DataFrame(columns=['manager_a', 'manager_b', 'matches_played', 'wins_a', 'draws', 'wins_b'])
        df_manager.to_csv(DATA_PATHS['manager_h2h'], index=False)
        print(f"Created new database: {DATA_PATHS['manager_h2h']}")

    # Stadiums Template
    if not os.path.exists(DATA_PATHS['stadiums']):
        df_stadiums = pd.DataFrame(columns=['team', 'stadium_name', 'capacity', 'average_attendance'])
        df_stadiums.to_csv(DATA_PATHS['stadiums'], index=False)
        print(f"Created new database: {DATA_PATHS['stadiums']}")

    # Matches Database (Consolidated)
    if not os.path.exists(DATA_PATHS['matches_db']):
        df_matches = pd.DataFrame(columns=['date', 'home_team', 'away_team', 'score_home', 'score_away', 'competition', 'season'])
        df_matches.to_csv(DATA_PATHS['matches_db'], index=False)
        print(f"Created new database: {DATA_PATHS['matches_db']}")

if __name__ == "__main__":
    initialize_new_datasets()
    print("Data structures initialized.")
