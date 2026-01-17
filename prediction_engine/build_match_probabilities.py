import pandas as pd
import numpy as np
import logging
from datetime import datetime
from .config import MODEL_WEIGHTS, DATA_PATHS
from .data_loader import load_existing_data, initialize_new_datasets

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_form_score(matches_df, team_name, n_matches=5):
    """
    Calculates a form score based on the last N matches.
    """
    if matches_df.empty:
        return 0.0
        
    # Filter for team (Home or Away)
    team_matches = matches_df[
        (matches_df['opponent'].notna()) # Basic check, assuming structure
    ].copy()
    
    # Sort by date
    if 'date' in team_matches.columns:
        team_matches['date'] = pd.to_datetime(team_matches['date'])
        team_matches = team_matches.sort_values('date', ascending=False)
    
    last_n = team_matches.head(n_matches)
    if last_n.empty:
        return 0.0
        
    points = 0
    total_possible = len(last_n) * 3
    
    for _, match in last_n.iterrows():
        res = match.get('result', '') # W, D, L
        if res == 'W':
            points += 3
        elif res == 'D':
            points += 1
            
    return (points / total_possible) if total_possible > 0 else 0.0

def calculate_match_proba(home_team, away_team, existing_data, new_data_manager=None, context=None):
    """
    Core engine function to calculate probabilities.
    """
    # 1. Base Probability (Neutral)
    p_home = 0.35
    p_draw = 0.30
    p_away = 0.35
    
    score_home = 0.0
    score_away = 0.0
    
    # 2. Standings & Elo Proxy (PPM)
    standings = existing_data.get('standings', pd.DataFrame())
    if not standings.empty:
        home_row = standings[standings['team'] == home_team]
        away_row = standings[standings['team'] == away_team]
        
        if not home_row.empty and not away_row.empty:
            home_ppm = float(home_row['points_per_match'].values[0])
            away_ppm = float(away_row['points_per_match'].values[0])
            
            diff_ppm = home_ppm - away_ppm
            impact = diff_ppm * MODEL_WEIGHTS['standings']['ppm_difference_weight']
            
            # Add to score (arbitrary scale, will normalize later)
            score_home += impact
            score_away -= impact

    # 3. Recent Form (OL specific since we have OL data primarily)
    # Ideally we need full league data. For this engine, we use what we have.
    # If home_team is OL, use OL matches.
    ol_matches = existing_data.get('ol_matches', pd.DataFrame())
    
    if home_team in ['Lyon', 'Olympique Lyonnais']:
        form_5 = calculate_form_score(ol_matches, home_team, 5)
        score_home += (form_5 - 0.5) * 10 * MODEL_WEIGHTS['recent_form']['last_5']
    elif away_team in ['Lyon', 'Olympique Lyonnais']:
        form_5 = calculate_form_score(ol_matches, away_team, 5)
        score_away += (form_5 - 0.5) * 10 * MODEL_WEIGHTS['recent_form']['last_5']
        
    # 4. Venue & Crowd
    # Default Home Advantage
    score_home += 5.0 * MODEL_WEIGHTS['venue_impact']['home_advantage_base']
    
    # 5. Absences
    absences = existing_data.get('absences', pd.DataFrame())
    # This would need a list of CURRENTLY absent players to be passed in `context`
    # For now, we simulate logic:
    if context and 'absent_players' in context:
        for player in context['absent_players']:
            # Find player impact
            impact_row = absences[absences['player'] == player]
            if not impact_row.empty:
                penalty = float(impact_row['impact_points'].values[0])
                # If player is from Home team, subtract from Home score, etc.
                # Assuming context specifies team
                if context['absent_team'] == home_team:
                    score_home -= penalty * MODEL_WEIGHTS['squad_impact']['key_player_absence']
                else:
                    score_away -= penalty * MODEL_WEIGHTS['squad_impact']['key_player_absence']

    # 6. Convert Scores to Probabilities (Softmax-ish or Sigmoid logic)
    # Simple logic: difference in scores shifts the probability
    
    diff = score_home - score_away
    # Sigmoid function to shift 35/30/35 distribution
    # shift = 1 / (1 + np.exp(-diff/10)) ... simplified linear shift for MVP
    
    shift = diff * 1.5 # 1 point diff = 1.5% shift
    
    p_home += (shift / 100)
    p_away -= (shift / 100)
    
    # Normalize
    total = p_home + p_draw + p_away
    p_home /= total
    p_draw /= total
    p_away /= total
    
    return {
        "home_team": home_team,
        "away_team": away_team,
        "prob_home": round(p_home * 100, 1),
        "prob_draw": round(p_draw * 100, 1),
        "prob_away": round(p_away * 100, 1),
        "details": {
            "score_home": round(score_home, 2),
            "score_away": round(score_away, 2)
        }
    }

def run_prediction_pipeline():
    logging.info("Initializing Prediction Engine...")
    initialize_new_datasets()
    
    logging.info("Loading Data...")
    data = load_existing_data()
    
    # Example Simulation: OL vs Marseille
    logging.info("Running Simulation: OL vs Marseille (Home)...")
    
    # Context for absences (Example)
    context = {
        "absent_players": ["Alexandre Lacazette"], # Hypothetical
        "absent_team": "Lyon"
    }
    
    result = calculate_match_proba("Lyon", "Marseille", data, context=context)
    
    logging.info(f"Result: {result}")
    
    # Save to CSV
    df_res = pd.DataFrame([result])
    df_res.to_csv(DATA_PATHS['predictions_output'], index=False)
    logging.info(f"Predictions saved to {DATA_PATHS['predictions_output']}")

if __name__ == "__main__":
    run_prediction_pipeline()
