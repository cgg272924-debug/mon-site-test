from dataclasses import dataclass
from typing import Dict, Any
import math

# Moteur central et explicable de probabilités de match pour l’Olympique Lyonnais.
# Philosophie : agréger quelques facteurs simples, normalisés entre -1 et +1
# (absences, forme récente, domicile/extérieur, classement, historique direct,
# solidité de l’adversaire) avec des pondérations dynamiques faciles à ajuster.
# Ce fichier est la seule source de vérité pour le score global et les
# probabilités (victoire / nul / défaite) ; tous les scripts amont doivent
# uniquement construire un MatchContext et appeler compute_match_prediction.


@dataclass
class MatchContext:
    opponent: str
    is_home: bool
    # Absences
    key_absences_count: int
    key_absences_impact: float
    # Forme récente (PPM)
    ppm_last_5: float
    ppm_last_10: float
    opp_ppm_last_5: float
    opp_ppm_last_10: float
    # Classement
    ol_rank: int
    opp_rank: int
    ol_home_rank: int
    ol_away_rank: int
    opp_home_rank: int
    opp_away_rank: int
    # Historique confrontations directes
    h2h_win_rate_5: float
    h2h_loss_rate_5: float
    h2h_matches_5: int
    # Adversaire vs équipes fortes
    opp_vs_top_teams_ppm: float
    league_ppm_top_threshold: float
    # Force de la composition (net LineupImpact normalisé entre -1 et +1)
    lineup_strength_score: float = 0.0


def _clamp(value: float, min_value: float = -1.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def score_absences(ctx: MatchContext) -> float:
    raw = -(ctx.key_absences_impact + ctx.key_absences_count * 0.5)
    score = raw / 5.0
    return _clamp(score)


def score_form(ctx: MatchContext) -> float:
    ol_avg = (ctx.ppm_last_5 + ctx.ppm_last_10) / 2.0
    opp_avg = (ctx.opp_ppm_last_5 + ctx.opp_ppm_last_10) / 2.0
    diff = ol_avg - opp_avg
    score = diff / 3.0
    return _clamp(score)


def score_home_away(ctx: MatchContext) -> float:
    if ctx.is_home:
        score = 0.25
    else:
        score = -0.25
    return _clamp(score)


def score_standings(ctx: MatchContext) -> float:
    rank_diff = ctx.opp_rank - ctx.ol_rank
    norm_rank = rank_diff / 10.0
    if ctx.is_home:
        ctx_ol = ctx.ol_home_rank
        ctx_opp = ctx.opp_away_rank
    else:
        ctx_ol = ctx.ol_away_rank
        ctx_opp = ctx.opp_home_rank
    ctx_diff = ctx_opp - ctx_ol
    norm_ctx = ctx_diff / 10.0
    score = (norm_rank + norm_ctx) / 2.0
    return _clamp(score)


def score_h2h(ctx: MatchContext) -> float:
    if ctx.h2h_matches_5 <= 0:
        return 0.0
    balance = ctx.h2h_win_rate_5 - ctx.h2h_loss_rate_5
    score = balance
    return _clamp(score)


def score_opponent_vs_strong(ctx: MatchContext) -> float:
    diff = ctx.opp_vs_top_teams_ppm - ctx.league_ppm_top_threshold
    score = -diff / 2.0
    return _clamp(score)


def score_lineup(ctx: MatchContext) -> float:
    return _clamp(ctx.lineup_strength_score)


def compute_dynamic_weights(absence_score: float) -> Dict[str, float]:
    if absence_score < -0.4:
        weights = {
            "absences": 0.4,
            "form": 0.18,
            "home_away": 0.1,
            "standings": 0.14,
            "h2h": 0.04,
            "opp_vs_strong": 0.04,
            "lineup": 0.1,
        }
    else:
        weights = {
            "absences": 0.18,
            "form": 0.27,
            "home_away": 0.18,
            "standings": 0.14,
            "h2h": 0.09,
            "opp_vs_strong": 0.04,
            "lineup": 0.1,
        }
    return weights


def aggregate_scores(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    total = 0.0
    for key, value in scores.items():
        w = weights.get(key, 0.0)
        total += value * w
    return _clamp(total)


def logits_to_probabilities(global_score: float) -> Dict[str, float]:
    scale = 2.0
    x = global_score * scale
    home_logit = x
    away_logit = -x
    draw_logit = -abs(x)
    home_exp = math.exp(home_logit)
    draw_exp = math.exp(draw_logit)
    away_exp = math.exp(away_logit)
    total = home_exp + draw_exp + away_exp
    return {
        "win": home_exp / total,
        "draw": draw_exp / total,
        "loss": away_exp / total,
    }


def explain_scores(ctx: MatchContext, scores: Dict[str, float], weights: Dict[str, float]) -> str:
    reasons = []
    abs_score = scores.get("absences", 0.0)
    if abs_score <= -0.4:
        reasons.append("Absences importantes dans l’effectif (facteur dominant).")
    elif abs_score < 0.0:
        reasons.append("Quelques absences pénalisent légèrement l’équipe.")
    else:
        reasons.append("Effectif quasiment au complet, peu d’impact des absences.")
    form_score = scores.get("form", 0.0)
    if form_score >= 0.3:
        reasons.append("Forme récente nettement favorable à l’OL.")
    elif form_score <= -0.3:
        reasons.append("Forme récente défavorable par rapport à l’adversaire.")
    venue_score = scores.get("home_away", 0.0)
    if venue_score > 0:
        reasons.append("Match à domicile au Groupama Stadium.")
    else:
        reasons.append("Match à l’extérieur.")
    standings_score = scores.get("standings", 0.0)
    if standings_score >= 0.3:
        reasons.append("Classement global et contextuel nettement à l’avantage de l’OL.")
    elif standings_score <= -0.3:
        reasons.append("Classement global ou contextuel plutôt favorable à l’adversaire.")
    h2h_score = scores.get("h2h", 0.0)
    if h2h_score >= 0.2:
        reasons.append("Historique des confrontations récent favorable.")
    elif h2h_score <= -0.2:
        reasons.append("Historique des confrontations récent défavorable.")
    opp_score = scores.get("opp_vs_strong", 0.0)
    if opp_score <= -0.2:
        reasons.append("Adversaire performant contre les équipes fortes.")
    elif opp_score >= 0.2:
        reasons.append("Adversaire en difficulté contre les équipes fortes.")
    lineup_score = scores.get("lineup", 0.0)
    if lineup_score >= 0.4:
        reasons.append("Composition très proche du meilleur onze disponible.")
    elif lineup_score >= 0.15:
        reasons.append("Composition globalement compétitive malgré quelques ajustements.")
    elif lineup_score <= -0.4:
        reasons.append("Onze fortement affaibli par les rotations ou absences majeures.")
    elif lineup_score <= -0.15:
        reasons.append("Onze légèrement affaibli par rapport au meilleur potentiel.")
    if weights["absences"] > weights["form"]:
        reasons.append("Les absences sont pondérées comme facteur principal dans ce contexte.")
    else:
        reasons.append("La forme récente et le contexte domicile/extérieur dominent la pondération.")
    return " ".join(reasons)


def compute_match_prediction(ctx: MatchContext) -> Dict[str, Any]:
    scores = {
        "absences": score_absences(ctx),
        "form": score_form(ctx),
        "home_away": score_home_away(ctx),
        "standings": score_standings(ctx),
        "h2h": score_h2h(ctx),
        "opp_vs_strong": score_opponent_vs_strong(ctx),
        "lineup": score_lineup(ctx),
    }
    absence_score = scores["absences"]
    weights = compute_dynamic_weights(absence_score)
    global_score = aggregate_scores(scores, weights)
    probabilities = logits_to_probabilities(global_score)
    explanation = explain_scores(ctx, scores, weights)
    return {
        "scores": scores,
        "weights": weights,
        "global_score": global_score,
        "probabilities": probabilities,
        "explanation": explanation,
        "proba_win": probabilities["win"],
        "proba_draw": probabilities["draw"],
        "proba_loss": probabilities["loss"],
        "engine_explanation": explanation,
    }


if __name__ == "__main__":
    example = MatchContext(
        opponent="Brest",
        is_home=True,
        key_absences_count=1,
        key_absences_impact=1.5,
        ppm_last_5=2.3,
        ppm_last_10=2.0,
        opp_ppm_last_5=1.4,
        opp_ppm_last_10=1.3,
        ol_rank=5,
        opp_rank=11,
        ol_home_rank=5,
        ol_away_rank=6,
        opp_home_rank=10,
        opp_away_rank=13,
        h2h_win_rate_5=0.5,
        h2h_loss_rate_5=0.2,
        h2h_matches_5=5,
        opp_vs_top_teams_ppm=0.9,
        league_ppm_top_threshold=1.6,
    )
    result = compute_match_prediction(example)
    print("Probabilités:", result["probabilities"])
    print("Explication:", result["explanation"])
