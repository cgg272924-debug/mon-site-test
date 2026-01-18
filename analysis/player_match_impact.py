import ast
from pathlib import Path

import numpy as np
import pandas as pd

print("=== IMPACT INDIVIDUEL JOUEURS SUR RÉSULTATS OL (ON/OFF) ===")

DATA_DIR = Path("data/processed")

matches_path = DATA_DIR / "ol_matches_with_match_key.csv"
lineups_path = DATA_DIR / "ol_match_lineups.csv"

if not matches_path.exists() or not lineups_path.exists():
    raise FileNotFoundError("Fichiers nécessaires manquants pour calculer l’impact joueurs.")

df_matches = pd.read_csv(matches_path)
df_lineups = pd.read_csv(lineups_path)

if "points" not in df_matches.columns:
    if "result" not in df_matches.columns:
        raise ValueError("Ni 'points' ni 'result' présents dans les matchs.")

    def result_to_points(r: str) -> int:
        if r == "W":
            return 3
        if r == "D":
            return 1
        return 0

    df_matches["points"] = df_matches["result"].apply(result_to_points)

df_merged = pd.merge(
    df_lineups,
    df_matches[["match_key", "points"]],
    on="match_key",
    how="inner",
)

if df_merged.empty:
    raise ValueError("Impossible de fusionner lineups et matchs pour calculer l’impact.")

all_players: set[str] = set()
for players_str in df_merged["players"]:
    try:
        player_list = ast.literal_eval(players_str)
        all_players.update(player_list)
    except Exception:
        continue

global_avg = df_merged["points"].mean()

rows = []

for player in sorted(all_players):
    matches_with = []
    matches_without = []

    for _, row in df_merged.iterrows():
        try:
            p_list = ast.literal_eval(row["players"])
        except Exception:
            continue
        if player in p_list:
            matches_with.append(row["points"])
        else:
            matches_without.append(row["points"])

    if not matches_with:
        continue

    avg_with = float(np.mean(matches_with))
    if matches_without:
        avg_without = float(np.mean(matches_without))
    else:
        avg_without = float(global_avg * 0.5)

    impact = avg_with - avg_without

    rows.append(
        {
            "player": player,
            "points_per_match_with": round(avg_with, 2),
            "points_per_match_without": round(avg_without, 2),
            "impact_ppm": round(impact, 2),
        }
    )

df_impact = pd.DataFrame(rows)
df_impact = df_impact.sort_values("impact_ppm", ascending=False)

out_path = DATA_DIR / "ol_player_match_impact.csv"
df_impact.to_csv(out_path, index=False)

print(f"Joueurs analysés : {len(df_impact)}")
print(f"Fichier créé : {out_path}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
