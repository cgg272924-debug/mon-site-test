import pandas as pd
from itertools import combinations

print("=== STEP 2 — GENERATION DES COMBINAISONS ===")

lineups = pd.read_csv("data/processed/ol_lineups_by_match.csv")

print("Lineups chargées :", lineups.shape)

rows = []

for match_key, group in lineups.groupby("match_key"):
    players = sorted(group["player"].dropna().unique())

    for size in [2, 3, 4, 5]:
        if len(players) >= size:
            for combo in combinations(players, size):
                rows.append(
                    {
                        "match_key": match_key,
                        "combo": " + ".join(combo),
                        "size": size,
                    }
                )

df_combos = pd.DataFrame(rows)

df_combos.to_csv(
    "data/processed/ol_lineup_combinations.csv",
    index=False,
)

print("Combinaisons générées :", df_combos.shape)
print("📁 Fichier créé : data/processed/ol_lineup_combinations.csv")
print("=== STEP 2 TERMINÉ ===")
