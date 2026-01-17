import pandas as pd
from itertools import combinations

print("=== STEP 2 — CREATION COMBINAISONS DE JOUEURS ===")

# ------------------------
# LOAD LINEUPS
# ------------------------
df = pd.read_csv("data/processed/ol_lineups_by_match.csv")
print("Lineups chargés :", df.shape)

# ------------------------
# GENERATE COMBINATIONS
# ------------------------
rows = []

for match_key, group in df.groupby("match_key"):
    players = sorted(group["player"].unique())

    for size in [2, 3, 4]:
        if len(players) >= size:
            for combo in combinations(players, size):
                rows.append({
                    "match_key": match_key,
                    "combo": " + ".join(combo),
                    "size": size
                })

# ------------------------
# CREATE DATAFRAME
# ------------------------
combos_df = pd.DataFrame(rows)

print("Combinaisons créées :", combos_df.shape)

# ------------------------
# SAVE
# ------------------------
combos_df.to_csv(
    "data/processed/ol_lineup_combinations.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_lineup_combinations.csv")
print("=== STEP 2 TERMINÉ ===")
