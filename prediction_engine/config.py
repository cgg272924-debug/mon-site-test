# Configuration and Weights for the Match Prediction Engine
# This file defines the weights used in the probability calculation model.
# Being a "White Box" model, all factors are transparent here.

MODEL_WEIGHTS = {
    "recent_form": {
        "last_5": 0.35,
        "last_10": 0.15,
        "last_15": 0.05
    },
    "squad_impact": {
        "key_player_absence": 2.0,  # Penalty points per key player absent
        "standard_player_absence": 0.5
    },
    "venue_impact": {
        "home_advantage_base": 1.10, # Multiplier
        "crowd_boost_high": 1.05,    # Extra multiplier for high attendance (>40k)
        "crowd_boost_medium": 1.02,
        "away_disadvantage": 0.90
    },
    "standings": {
        "rank_difference_weight": 0.1, # Points per rank position difference
        "ppm_difference_weight": 20.0  # Points per PPM difference
    },
    "history": {
        "h2h_last_5_weight": 0.15,
        "rivalry_bonus": 0.05 # Multiplier for motivation in derbies
    },
    "manager": {
        "h2h_win_rate_weight": 0.1
    }
}

# CSV Paths (New architecture)
DATA_PATHS = {
    "matches_db": "prediction_engine/data/matches_database.csv",
    "manager_h2h": "prediction_engine/data/manager_h2h.csv",
    "stadiums": "prediction_engine/data/stadiums.csv",
    "predictions_output": "prediction_engine/data/match_predictions.csv"
}
