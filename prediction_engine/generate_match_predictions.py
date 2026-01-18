import sys
from pathlib import Path

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from prediction_engine.build_match_probabilities import TeamFeatures, compute_match_probabilities
from prediction_engine.config import DATA_PATHS


def build_lyon_brest_example() -> Path:
    home = TeamFeatures(
        ppm_last_5=2.4,
        ppm_last_10=2.1,
        ppm_last_15=2.0,
        missing_key_players=0,
        missing_other_players=1,
        is_home=True,
        crowd_level="high",
        rank_overall=3,
        rank_context=3,
        ppm_overall=2.1,
        ppm_context=2.2,
        h2h_wins_last_5=3,
        h2h_draws_last_5=1,
        h2h_losses_last_5=1,
        rivalry_level=0.7,
        manager_h2h_win_rate=0.6,
    )
    away = TeamFeatures(
        ppm_last_5=1.4,
        ppm_last_10=1.3,
        ppm_last_15=1.2,
        missing_key_players=2,
        missing_other_players=1,
        is_home=False,
        crowd_level="medium",
        rank_overall=10,
        rank_context=9,
        ppm_overall=1.3,
        ppm_context=1.4,
        h2h_wins_last_5=1,
        h2h_draws_last_5=1,
        h2h_losses_last_5=3,
        rivalry_level=0.7,
        manager_h2h_win_rate=0.4,
    )
    result = compute_match_probabilities(home, away)
    out_path = Path(DATA_PATHS["predictions_output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        [
            {
                "home_team": "Lyon",
                "away_team": "Brest",
                "proba_home_win": result["home_win"],
                "proba_draw": result["draw"],
                "proba_away_win": result["away_win"],
                "home_strength": result["home_strength"],
                "away_strength": result["away_strength"],
                "margin": result["margin"],
            }
        ]
    )
    df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    path = build_lyon_brest_example()
    print(path)

