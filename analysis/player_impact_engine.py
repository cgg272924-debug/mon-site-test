from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd

from core_match_engine import MatchContext, compute_match_prediction


DATA_PROCESSED = Path("data/processed")


@dataclass
class PlayerImpact:
    player_id: str
    name: str
    pos: str
    impact_score: float
    impact_category: str
    minutes_played: float


def _load_players_rated() -> pd.DataFrame:
    path = DATA_PROCESSED / "ol_players_rated.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _load_key_players() -> pd.DataFrame:
    path = DATA_PROCESSED / "ol_key_players.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_on_off_impact() -> pd.DataFrame:
    path = DATA_PROCESSED / "ol_player_match_impact.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_combo_summary() -> pd.DataFrame:
    path = DATA_PROCESSED / "ol_combo_impact_summary.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _normalize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if s.empty:
        return s
    min_val = s.min()
    max_val = s.max()
    if max_val == min_val:
        return pd.Series([0.0] * len(s), index=s.index)
    return (s - min_val) / (max_val - min_val)


def _categorize_impact(score: float) -> str:
    if score >= 80.0:
        return "leader"
    if score >= 65.0:
        return "titulaire_clé"
    if score >= 50.0:
        return "titulaire"
    if score >= 30.0:
        return "rotation"
    return "faible_impact"


def build_player_impact_table() -> pd.DataFrame:
    df_rated = _load_players_rated()
    df_keys = _load_key_players()
    df_impact = _load_on_off_impact()
    df_combo = _load_combo_summary()

    df = df_rated.copy()
    df = df.merge(
        df_keys[["player", "importance"]],
        on="player",
        how="left",
        suffixes=("", "_key"),
    )
    df = df.merge(
        df_impact[["player", "impact_ppm"]],
        on="player",
        how="left",
    )

    combo_score = pd.Series(0.0, index=df.index)
    if not df_combo.empty:
        combo_rows: list[dict[str, float | str]] = []
        for _, row in df_combo.iterrows():
            combo_str = str(row.get("combo", ""))
            if not combo_str:
                continue
            players = [p.strip() for p in combo_str.split("+")]
            try:
                matches = float(row.get("matches", 0.0))
                avg_points = float(row.get("avg_points", 0.0))
            except Exception:
                continue
            for name in players:
                combo_rows.append(
                    {
                        "player": name,
                        "matches": matches,
                        "avg_points": avg_points,
                    }
                )

        if combo_rows:
            df_combo_long = pd.DataFrame(combo_rows)
            df_combo_long["points_weighted"] = (
                df_combo_long["avg_points"] * df_combo_long["matches"]
            )
            df_player_combo = (
                df_combo_long.groupby("player")
                .agg(
                    combo_points=("points_weighted", "sum"),
                    combo_matches=("matches", "sum"),
                )
                .reset_index()
            )
            df_player_combo["combo_score_raw"] = (
                df_player_combo["combo_points"] / df_player_combo["combo_matches"]
            )
            combo_map = df_player_combo.set_index("player")["combo_score_raw"]
            combo_score = df["player"].map(combo_map).fillna(0.0)

    df["Playing Time_Min"] = df["Playing Time_Min"].astype(float)
    minutes_norm = _normalize_series(df["Playing Time_Min"])

    gls_n = df.get("gls_n", pd.Series(0.0, index=df.index)).astype(float)
    xg_n = df.get("xg_n", pd.Series(0.0, index=df.index)).astype(float)
    xag_n = df.get("xag_n", pd.Series(0.0, index=df.index)).astype(float)
    prgc_n = df.get("prgc_n", pd.Series(0.0, index=df.index)).astype(float)
    prgp_n = df.get("prgp_n", pd.Series(0.0, index=df.index)).astype(float)
    prgr_n = df.get("prgr_n", pd.Series(0.0, index=df.index)).astype(float)

    df["importance"] = df["importance"].fillna(0.0)
    importance_norm = _normalize_series(df["importance"])

    impact_ppm = df.get("impact_ppm", pd.Series(0.0, index=df.index)).astype(float)
    impact_ppm_norm = _normalize_series(impact_ppm)

    combo_score_norm = _normalize_series(combo_score)

    attack_score = 0.4 * gls_n + 0.3 * xg_n + 0.3 * xag_n

    def _def_multiplier(pos: str) -> float:
        p = (pos or "").upper()
        if "GK" in p:
            return 1.1
        if "DF" in p or "CB" in p or "LB" in p or "RB" in p:
            return 1.2
        if "DM" in p:
            return 1.2
        if "MF" in p:
            return 1.0
        return 0.7

    mult = df["pos"].astype(str).apply(_def_multiplier)
    defense_base = 0.4 * prgc_n + 0.3 * prgp_n + 0.3 * prgr_n
    defense_score = (defense_base * mult).clip(0.0, 1.0)

    tactical_score = importance_norm

    minutes_score = minutes_norm
    on_off_score = impact_ppm_norm
    combo_score_final = combo_score_norm

    w_minutes = 0.15
    w_attack = 0.2
    w_defense = 0.2
    w_onoff = 0.2
    w_tactical = 0.1
    w_combo = 0.15
    total_w = (
        w_minutes + w_attack + w_defense + w_onoff + w_tactical + w_combo
    )

    raw_score = (
        w_minutes * minutes_score
        + w_attack * attack_score
        + w_defense * defense_score
        + w_onoff * on_off_score
        + w_tactical * tactical_score
        + w_combo * combo_score_final
    ) / total_w

    impact_score = (raw_score * 100.0).clip(0.0, 100.0)

    df_out = pd.DataFrame(
        {
            "player_id": df["player"],
            "name": df["player"],
            "pos": df["pos"],
            "minutes_played": df["Playing Time_Min"],
            "impact_score": impact_score.round(1),
        }
    )
    df_out["impact_category"] = df_out["impact_score"].apply(_categorize_impact)
    return df_out


def compute_lineup_impact(
    lineup_players: List[str],
    impact_table: pd.DataFrame,
    key_player_threshold: float = 70.0,
) -> Dict[str, Any]:
    df = impact_table.copy()
    df["name_lower"] = df["name"].str.lower()
    lineup_set = {p.lower() for p in lineup_players}

    df_lineup = df[df["name_lower"].isin(lineup_set)].copy()
    if df_lineup.empty:
        lineup_strength_score = 0.0
        absence_penalty = 0.0
        explanation = "Composition inconnue ou non couverte par la table d’impact joueurs."
        return {
            "lineup_strength_score": lineup_strength_score,
            "lineup_impact_raw": 0.0,
            "absence_penalty": absence_penalty,
            "net_lineup_impact": lineup_strength_score,
            "missing_key_players": [],
            "used_players": [],
            "lineup_explanation": explanation,
        }

    all_top = df.sort_values("impact_score", ascending=False).head(11)
    baseline_sum = float(all_top["impact_score"].sum())
    lineup_sum = float(df_lineup["impact_score"].sum())

    if baseline_sum <= 0.0:
        ratio = 1.0
    else:
        ratio = lineup_sum / baseline_sum

    lineup_strength_score = (ratio - 1.0) / 0.3
    if lineup_strength_score > 1.0:
        lineup_strength_score = 1.0
    if lineup_strength_score < -1.0:
        lineup_strength_score = -1.0

    df_keys = df[df["impact_score"] >= key_player_threshold].copy()
    key_names = set(df_keys["name_lower"].tolist())
    missing_keys = sorted(list(key_names - lineup_set))

    if df_keys.empty:
        absence_penalty = 0.0
    else:
        missing_score = df_keys[df_keys["name_lower"].isin(missing_keys)][
            "impact_score"
        ].sum()
        total_key_score = df_keys["impact_score"].sum()
        if total_key_score <= 0.0:
            absence_penalty = 0.0
        else:
            absence_penalty = float(missing_score / total_key_score)

    net_lineup_impact = lineup_strength_score - absence_penalty
    if net_lineup_impact > 1.0:
        net_lineup_impact = 1.0
    if net_lineup_impact < -1.0:
        net_lineup_impact = -1.0

    explanation_parts: List[str] = []
    if missing_keys:
        missing_labels = df[df["name_lower"].isin(missing_keys)][["name", "pos"]]
        missing_labels_list = [
            f"{row['name']} ({row['pos']})" for _, row in missing_labels.iterrows()
        ]
        if len(missing_labels_list) == 1:
            names_text = missing_labels_list[0]
        elif len(missing_labels_list) == 2:
            names_text = " et ".join(missing_labels_list)
        else:
            names_text = ", ".join(missing_labels_list[:-1]) + " et " + missing_labels_list[-1]

        def _role_bucket(pos: str) -> str:
            p = (pos or "").upper()
            if "GK" in p:
                return "gardien"
            if "DF" in p or "CB" in p or "LB" in p or "RB" in p:
                return "défensif"
            if "DM" in p or "MF" in p:
                return "milieu"
            return "offensif"

        roles = [_role_bucket(str(row["pos"])) for _, row in missing_labels.iterrows()]
        if roles.count("défensif") >= max(1, len(roles) // 2):
            zone = "défensif"
        elif roles.count("offensif") >= max(1, len(roles) // 2):
            zone = "offensif"
        elif roles.count("milieu") >= max(1, len(roles) // 2):
            zone = "au milieu"
        else:
            zone = "global"

        if zone == "global":
            explanation_parts.append(
                f"L’absence de {names_text} réduit l’équilibre global de l’OL."
            )
        else:
            explanation_parts.append(
                f"L’absence de {names_text} réduit l’impact {zone} de l’OL."
            )
    else:
        explanation_parts.append(
            "Composition proche du meilleur onze disponible, sans absence majeure."
        )

    if lineup_strength_score >= 0.4:
        explanation_parts.append(
            "Le onze de départ affiche une forte cohérence collective."
        )
    elif lineup_strength_score <= -0.4:
        explanation_parts.append(
            "Le onze de départ est nettement en dessous du potentiel maximal de l’effectif."
        )

    explanation = " ".join(explanation_parts)

    return {
        "lineup_strength_score": float(net_lineup_impact),
        "lineup_impact_raw": float(lineup_strength_score),
        "absence_penalty": float(absence_penalty),
        "net_lineup_impact": float(net_lineup_impact),
        "missing_key_players": missing_keys,
        "used_players": sorted(df_lineup["name"].tolist()),
        "lineup_explanation": explanation,
    }


def build_match_context_with_lineup(
    base_context: MatchContext, lineup_strength_score: float
) -> MatchContext:
    return MatchContext(
        opponent=base_context.opponent,
        is_home=base_context.is_home,
        key_absences_count=base_context.key_absences_count,
        key_absences_impact=base_context.key_absences_impact,
        ppm_last_5=base_context.ppm_last_5,
        ppm_last_10=base_context.ppm_last_10,
        opp_ppm_last_5=base_context.opp_ppm_last_5,
        opp_ppm_last_10=base_context.opp_ppm_last_10,
        ol_rank=base_context.ol_rank,
        opp_rank=base_context.opp_rank,
        ol_home_rank=base_context.ol_home_rank,
        ol_away_rank=base_context.ol_away_rank,
        opp_home_rank=base_context.opp_home_rank,
        opp_away_rank=base_context.opp_away_rank,
        h2h_win_rate_5=base_context.h2h_win_rate_5,
        h2h_loss_rate_5=base_context.h2h_loss_rate_5,
        h2h_matches_5=base_context.h2h_matches_5,
        opp_vs_top_teams_ppm=base_context.opp_vs_top_teams_ppm,
        league_ppm_top_threshold=base_context.league_ppm_top_threshold,
        lineup_strength_score=lineup_strength_score,
    )


def save_player_impact_table(path: Path | None = None) -> Path:
    df = build_player_impact_table()
    out_path = path or (DATA_PROCESSED / "ol_player_impact_scores.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    table = build_player_impact_table()
    out = save_player_impact_table()
    print(f"Table d’impact joueurs sauvegardée dans {out}")
    print(table.head())
