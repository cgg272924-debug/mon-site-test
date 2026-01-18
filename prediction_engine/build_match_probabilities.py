from dataclasses import dataclass
from typing import Dict
import math
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from prediction_engine.config import MODEL_WEIGHTS

PROBABILITY_SHARPNESS = 1.0
DRAW_STABILITY = 0.8

@dataclass
class TeamFeatures:
    ppm_last_5: float
    ppm_last_10: float
    ppm_last_15: float
    missing_key_players: int
    missing_other_players: int
    is_home: bool
    crowd_level: str
    rank_overall: int
    rank_context: int
    ppm_overall: float
    ppm_context: float
    h2h_wins_last_5: int
    h2h_draws_last_5: int
    h2h_losses_last_5: int
    rivalry_level: float
    manager_h2h_win_rate: float

def _recent_form_points(team: TeamFeatures) -> float:
    weights = MODEL_WEIGHTS["recent_form"]
    value = 0.0
    value += team.ppm_last_5 * weights["last_5"]
    value += team.ppm_last_10 * weights["last_10"]
    value += team.ppm_last_15 * weights["last_15"]
    return value

def _squad_impact_penalty(team: TeamFeatures) -> float:
    weights = MODEL_WEIGHTS["squad_impact"]
    penalty = 0.0
    penalty += team.missing_key_players * weights["key_player_absence"]
    penalty += team.missing_other_players * weights["standard_player_absence"]
    return penalty

def _venue_multiplier(team: TeamFeatures, is_away: bool) -> float:
    weights = MODEL_WEIGHTS["venue_impact"]
    multiplier = 1.0
    if team.is_home:
        multiplier *= weights["home_advantage_base"]
        if team.crowd_level == "high":
            multiplier *= weights["crowd_boost_high"]
        elif team.crowd_level == "medium":
            multiplier *= weights["crowd_boost_medium"]
    if is_away:
        multiplier *= weights["away_disadvantage"]
    return multiplier

def _standings_points(team: TeamFeatures, league_size: int) -> float:
    weights = MODEL_WEIGHTS["standings"]
    rank_score = (league_size - team.rank_overall + 1) * weights["rank_difference_weight"]
    ppm_score = team.ppm_overall * weights["ppm_difference_weight"]
    return rank_score + ppm_score

def _history_points(home: TeamFeatures, away: TeamFeatures) -> Dict[str, float]:
    weights = MODEL_WEIGHTS["history"]
    total_h2h = home.h2h_wins_last_5 + home.h2h_draws_last_5 + home.h2h_losses_last_5
    if total_h2h == 0:
        balance = 0.0
    else:
        balance = (home.h2h_wins_last_5 - home.h2h_losses_last_5) / total_h2h
    home_points = balance * weights["h2h_last_5_weight"]
    away_points = -balance * weights["h2h_last_5_weight"]
    rivalry_factor = 1.0 + weights["rivalry_bonus"] * max(0.0, min(1.0, home.rivalry_level))
    return {
        "home_points": home_points,
        "away_points": away_points,
        "rivalry_factor": rivalry_factor,
    }

def _manager_points(home: TeamFeatures, away: TeamFeatures) -> Dict[str, float]:
    weights = MODEL_WEIGHTS["manager"]
    home_points = home.manager_h2h_win_rate * weights["h2h_win_rate_weight"]
    away_points = away.manager_h2h_win_rate * weights["h2h_win_rate_weight"]
    return {"home_points": home_points, "away_points": away_points}

def compute_team_strengths(home: TeamFeatures, away: TeamFeatures, league_size: int = 18) -> Dict[str, float]:
    home_score = 1.0
    away_score = 1.0
    home_score += _recent_form_points(home)
    away_score += _recent_form_points(away)
    home_score -= _squad_impact_penalty(home)
    away_score -= _squad_impact_penalty(away)
    home_score = max(home_score, 0.01)
    away_score = max(away_score, 0.01)
    home_score *= _venue_multiplier(home, is_away=False)
    away_score *= _venue_multiplier(away, is_away=not away.is_home)
    home_score += _standings_points(home, league_size)
    away_score += _standings_points(away, league_size)
    history = _history_points(home, away)
    home_score += history["home_points"]
    away_score += history["away_points"]
    home_score *= history["rivalry_factor"]
    away_score *= history["rivalry_factor"]
    manager = _manager_points(home, away)
    home_score += manager["home_points"]
    away_score += manager["away_points"]
    home_score = max(home_score, 0.01)
    away_score = max(away_score, 0.01)
    return {"home_strength": home_score, "away_strength": away_score}

def compute_match_probabilities(home: TeamFeatures, away: TeamFeatures, league_size: int = 18) -> Dict[str, float]:
    strengths = compute_team_strengths(home, away, league_size=league_size)
    home_strength = strengths["home_strength"]
    away_strength = strengths["away_strength"]
    margin = home_strength - away_strength
    score_home = math.exp(PROBABILITY_SHARPNESS * margin)
    score_away = math.exp(-PROBABILITY_SHARPNESS * margin)
    score_draw = math.exp(DRAW_STABILITY * (1.0 - abs(margin)))
    total = score_home + score_draw + score_away
    home_win = score_home / total
    draw = score_draw / total
    away_win = score_away / total
    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "home_strength": home_strength,
        "away_strength": away_strength,
        "margin": margin,
    }

if __name__ == "__main__":
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
    print(result)
