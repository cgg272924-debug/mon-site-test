import pandas as pd
import itertools

print("=== STEP 2 — COMBOS PAR MATCH (MATCH_KEY) ===")

lineups = pd.read_csv("data/processed/ol_lineups_by_match.csv")
matches = pd.read_csv("data/processed/ol_matches_with_match_key.csv")

print("Lineups chargées :", lineups.shape)
print("Matchs chargés  :", matches.shape)

matches_lookup = matches.set_index("match_key")

rows = []

for match_key, group in lineups.groupby("match_key"):
    if match_key not in matches_lookup.index:
        continue

    match_row = matches_lookup.loc[match_key]

    joueurs = sorted(group["player"].dropna().unique())

    if len(joueurs) < 2:
        continue

    for r in range(2, min(12, len(joueurs) + 1)):
        for combo in itertools.combinations(joueurs, r):
            rows.append(
                {
                    "match_key": match_key,
                    "combo": " + ".join(combo),
                    "size": r,
                    "points": match_row["points"],
                    "score_final": match_row["score_final"],
                }
            )

df = pd.DataFrame(rows)

print("Combos créés :", df.shape)

df.to_csv(
    "data/processed/ol_combos_per_match.csv",
    index=False,
)

print("📁 Fichier créé : data/processed/ol_combos_per_match.csv")
print("=== STEP 2 TERMINÉ ===")
