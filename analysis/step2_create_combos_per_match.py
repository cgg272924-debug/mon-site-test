import pandas as pd
import itertools

print("=== STEP 2 — COMBOS PAR MATCH (DATE EXTRACTION) ===")

players = pd.read_csv("data/processed/ol_player_minutes.csv")
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

# 🔧 EXTRACTION DATE DEPUIS 'game'
players["match_date"] = (
    players["game"]
    .astype(str)
    .str.extract(r"(\d{4}-\d{2}-\d{2})")[0]
)

players["match_date"] = pd.to_datetime(
    players["match_date"], errors="coerce"
).dt.date

# Dates matchs
matches["match_date"] = pd.to_datetime(
    matches["date"], errors="coerce"
).dt.date

print("Dates players uniques :", players["match_date"].nunique())
print("Dates matches uniques :", matches["match_date"].nunique())

rows = []

for match_date, group in players.groupby("match_date"):
    if pd.isna(match_date):
        continue

    match_row = matches[matches["match_date"] == match_date]

    if match_row.empty:
        continue

    match_row = match_row.iloc[0]

    joueurs = sorted(group["player"].dropna().unique())

    if len(joueurs) < 2:
        continue

    for r in range(2, min(12, len(joueurs) + 1)):
        for combo in itertools.combinations(joueurs, r):
            rows.append({
                "match_date": match_date,
                "combo": " + ".join(combo),
                "size": r,
                "points": match_row["points"],
                "score_final": match_row["score_final"]
            })

df = pd.DataFrame(rows)

print("Combos créés :", df.shape)

df.to_csv(
    "data/processed/ol_combos_per_match.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_combos_per_match.csv")
print("=== STEP 2 TERMINÉ ===")
