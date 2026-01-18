import pandas as pd
import numpy as np
from pathlib import Path
import ast
from core_match_engine import MatchContext, compute_match_prediction

# --- Configuration ---
DATA_DIR = Path("data/processed")
INPUT_FILES = {
    "standings": "league1_standings_home_away.csv",
    "proba_dataset": "ol_match_proba_dataset.csv",
    "injuries": "ol_injuries_transfermarkt.csv",
    "lineups": "ol_match_lineups.csv",
    "matches": "ol_matches_with_match_key.csv"
}
OUTPUT_FILE = DATA_DIR / "ol_next_match_simulation.csv"

# Weights for probability calculation
WEIGHTS = {
    "ppm_diff": 0.8,        # Points Per Match difference
    "rank_diff": 0.05,      # Rank difference
    "home_advantage": 0.3,  # Bonus for playing at home
    "h2h_recent": 0.2,      # Recent H2H influence
    "injury_factor": 1.5,   # Multiplier for injury impact points
    "rivalry": 0.2          # Penalty for high rivalry (harder matches)
}

LEAGUE_TOP_PPM_THRESHOLD = 1.7

def load_data():
    """Load all necessary CSV files."""
    data = {}
    for key, filename in INPUT_FILES.items():
        file_path = DATA_DIR / filename
        if file_path.exists():
            data[key] = pd.read_csv(file_path)
        else:
            print(f"Warning: {filename} not found.")
            data[key] = pd.DataFrame()
    return data

def calculate_player_impact(df_lineups, df_matches):
    """
    Calculate impact of each player on team performance (Points Per Match).
    Returns a dictionary: {player_name: impact_points}
    impact_points = (Avg Points WITH player) - (Avg Points WITHOUT player)
    """
    if df_lineups.empty or df_matches.empty:
        return {}

    # Merge lineups with match results
    df_merged = pd.merge(df_lineups, df_matches[['match_key', 'points']], on='match_key', how='inner')
    
    # Get all unique players
    all_players = set()
    for players_str in df_merged['players']:
        try:
            player_list = ast.literal_eval(players_str)
            all_players.update(player_list)
        except:
            continue
            
    player_stats = {}
    global_avg = df_merged['points'].mean()

    for player in all_players:
        # Filter matches with/without player
        # We need to parse the string list for each row. This is slow but fine for small datasets.
        matches_with = []
        matches_without = []
        
        for _, row in df_merged.iterrows():
            try:
                p_list = ast.literal_eval(row['players'])
                if player in p_list:
                    matches_with.append(row['points'])
                else:
                    matches_without.append(row['points'])
            except:
                continue
        
        if not matches_with:
            continue
            
        avg_with = np.mean(matches_with)
        # If player played all matches, compare to global avg or 0? 
        # Let's compare to global avg if matches_without is empty (which means he is crucial or always there)
        avg_without = np.mean(matches_without) if matches_without else (global_avg * 0.5) # Penalty if key player missing
        
        impact = avg_with - avg_without
        player_stats[player] = impact

    return player_stats

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def calculate_win_probability(row, ol_stats, injury_impact_sum, key_absences_count, proba_dataset, is_home=True):
    """
    Calculate win probability for OL against a specific opponent.
    row: Opponent stats row from standings
    ol_stats: OL stats row from standings
    """
    
    # 1. Team Strength Difference (Points Per Match)
    if is_home:
        ol_ppm = ol_stats["home_points_per_match"]
        opp_ppm = row["away_points_per_match"]
        home_bonus = WEIGHTS["home_advantage"]
    else:
        ol_ppm = ol_stats["away_points_per_match"]
        opp_ppm = row["home_points_per_match"]
        home_bonus = -WEIGHTS["home_advantage"]

    ppm_diff = ol_ppm - opp_ppm
    
    # 2. Rank Difference (Sign inverted: higher rank (smaller number) is better)
    rank_diff = row["rank"] - ol_stats["rank"]
    
    # 3. Injury Penalty
    injury_penalty = injury_impact_sum * WEIGHTS["injury_factor"]
    
    # 4. H2H & Rivalry
    h2h_bonus = 0.0
    rivalry_penalty = 0.0
    h2h_win_rate_5 = 0.0
    h2h_loss_rate_5 = 0.0
    h2h_matches_5 = 0
    ol_home_rank = int(ol_stats["rank"])
    ol_away_rank = int(ol_stats["rank"])
    opp_home_rank = int(row["rank"])
    opp_away_rank = int(row["rank"])
    opp_vs_top_teams_ppm = float(row.get("points_per_match", opp_ppm))
    
    if not proba_dataset.empty:
        opp_h2h = proba_dataset[proba_dataset["opponent"] == row["team"]]
        if not opp_h2h.empty:
            avg_h2h_win = opp_h2h["h2h5_win_rate"].mean()
            avg_h2h_loss = opp_h2h["h2h5_loss_rate"].mean()
            h2h_bonus = (avg_h2h_win - avg_h2h_loss) * WEIGHTS["h2h_recent"]
            h2h_win_rate_5 = float(avg_h2h_win)
            h2h_loss_rate_5 = float(avg_h2h_loss)
            if "h2h_matches_played" in opp_h2h.columns:
                h2h_matches_5 = int(opp_h2h["h2h_matches_played"].mean())
            if "rivalry_index" in opp_h2h.columns:
                avg_rivalry = opp_h2h["rivalry_index"].mean()
                if avg_rivalry > 0.5:
                    rivalry_penalty = avg_rivalry * WEIGHTS["rivalry"]
            if "ol_home_rank" in opp_h2h.columns:
                ol_home_rank = int(opp_h2h["ol_home_rank"].iloc[0])
            if "ol_away_rank" in opp_h2h.columns:
                ol_away_rank = int(opp_h2h["ol_away_rank"].iloc[0])
            if "opp_home_rank" in opp_h2h.columns:
                opp_home_rank = int(opp_h2h["opp_home_rank"].iloc[0])
            if "opp_away_rank" in opp_h2h.columns:
                opp_away_rank = int(opp_h2h["opp_away_rank"].iloc[0])

    # Get stats for UI comparison
    if is_home:
        ol_gf = ol_stats["home_goals_for_per_match"]
        ol_ga = ol_stats["home_goals_against_per_match"]
        opp_gf = row["away_goals_for_per_match"]
        opp_ga = row["away_goals_against_per_match"]
    else:
        ol_gf = ol_stats["away_goals_for_per_match"]
        ol_ga = ol_stats["away_goals_against_per_match"]
        opp_gf = row["home_goals_for_per_match"]
        opp_ga = row["home_goals_against_per_match"]

    # Output delegated to core_match_engine
    ctx = MatchContext(
        opponent=row["team"],
        is_home=bool(is_home),
        key_absences_count=int(key_absences_count),
        key_absences_impact=float(injury_impact_sum),
        ppm_last_5=float(ol_ppm),
        ppm_last_10=float(ol_stats.get("points_per_match", ol_ppm)),
        opp_ppm_last_5=float(opp_ppm),
        opp_ppm_last_10=float(row.get("points_per_match", opp_ppm)),
        ol_rank=int(ol_stats["rank"]),
        opp_rank=int(row["rank"]),
        ol_home_rank=int(ol_home_rank),
        ol_away_rank=int(ol_away_rank),
        opp_home_rank=int(opp_home_rank),
        opp_away_rank=int(opp_away_rank),
        h2h_win_rate_5=float(h2h_win_rate_5),
        h2h_loss_rate_5=float(h2h_loss_rate_5),
        h2h_matches_5=int(h2h_matches_5),
        opp_vs_top_teams_ppm=float(opp_vs_top_teams_ppm),
        league_ppm_top_threshold=float(LEAGUE_TOP_PPM_THRESHOLD),
    )
    engine_result = compute_match_prediction(ctx)
    proba = engine_result["probabilities"]
    global_score = engine_result["global_score"]
    proba_win = proba["win"]
    proba_draw = proba["draw"]
    proba_loss = proba["loss"]

    return pd.Series({
        "opponent": row["team"],
        "venue": "Home" if is_home else "Away",
        "proba_win": round(proba_win * 100, 1),
        "proba_draw": round(proba_draw * 100, 1),
        "proba_loss": round(proba_loss * 100, 1),
        "score_raw": round(global_score, 2),
        "injury_penalty": round(injury_penalty, 2),
        "ppm_diff": round(ppm_diff, 2),
        "h2h_bonus": round(h2h_bonus, 2),
        "rivalry_penalty": round(rivalry_penalty, 2),
        "ol_gf": round(ol_gf, 2),
        "ol_ga": round(ol_ga, 2),
        "opp_gf": round(opp_gf, 2),
        "opp_ga": round(opp_ga, 2),
        "ol_ppm": round(ol_ppm, 2),
        "opp_ppm": round(opp_ppm, 2),
        "engine_explanation": engine_result["explanation"],
    })

def main():
    print("=== OL MATCH WIN PROBABILITY SIMULATOR ===")
    
    data = load_data()
    if data['standings'].empty:
        print("Error: Standings data missing.")
        return

    # 1. Get OL Stats
    df_standings = data['standings']
    ol_stats = df_standings[df_standings['team'] == 'Lyon'].iloc[0]
    
    # 2. Calculate Player Impacts
    print("Calculating player impacts...")
    player_impacts = calculate_player_impact(data['lineups'], data['matches'])
    
    # 3. Calculate Current Injury Penalty
    print("Processing injuries...")
    current_injuries = []
    if not data['injuries'].empty:
        current_injuries = data['injuries']['player'].tolist()
    
    total_injury_impact = 0.0
    injured_details = []
    
    for player in current_injuries:
        # Match player name (fuzzy or direct)
        # Direct match for now
        impact = player_impacts.get(player, 0.0)
        # If player has negative impact (team plays better without him), ignore for injury penalty
        if impact > 0:
            total_injury_impact += impact
            injured_details.append(f"{player} ({impact:.2f})")
            
    key_absences_count = len(injured_details)
    print(f"Total Injury Impact Penalty: {total_injury_impact:.2f}")
    print(f"Key Absences: {', '.join(injured_details)}")

    # 4. Simulate Next Matches (vs All Opponents)
    print("Simulating probabilities vs all Ligue 1 opponents...")
    results = []
    
    # Filter out OL from opponents
    opponents = df_standings[df_standings['team'] != 'Lyon']
    
    for _, opp_row in opponents.iterrows():
        # Simulate HOME match
        res_home = calculate_win_probability(
            opp_row,
            ol_stats,
            total_injury_impact,
            key_absences_count,
            data["proba_dataset"],
            is_home=True,
        )
        results.append(res_home)
        
        # Simulate AWAY match
        res_away = calculate_win_probability(
            opp_row,
            ol_stats,
            total_injury_impact,
            key_absences_count,
            data["proba_dataset"],
            is_home=False,
        )
        results.append(res_away)

    df_results = pd.DataFrame(results)
    
    # Save results
    df_results.to_csv(OUTPUT_FILE, index=False)
    print(f"Simulation complete. Saved to {OUTPUT_FILE}")
    print("\nSample Predictions (Top 5):")
    print(df_results.head(10))

if __name__ == "__main__":
    main()
