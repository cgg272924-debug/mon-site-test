import pandas as pd

print("=== STEP 3 — IMPACT DES COMBINAISONS SUR LES RESULTATS ===")

# ------------------------
# LOAD FILES
# ------------------------
combos = pd.read_csv("data/processed/ol_lineup_combinations.csv")
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

print("Combinaisons :", combos.shape)
print("Matchs :", matches.shape)

# ------------------------
# PREPARE MATCH KEY
# ------------------------
matches["match_key"] = (
    matches["date"].astype(str)
    + "_" + matches["opponent"].astype(str)
    + "_" + matches["venue"].astype(str)
)

# ------------------------
# MERGE
# ------------------------
df = combos.merge(
    matches[["match_key", "points", "score_final"]],
    on="match_key",
    how="left"
)

df = df.dropna(subset=["points"])

print("Après merge :", df.shape)

# ------------------------
# AGGREGATION
# ------------------------
summary = (
    df.groupby(["combo", "size"])
    .agg(
        matches=("points", "count"),
        avg_points=("points", "mean"),
        avg_score=("score_final", "mean")
    )
    .reset_index()
)

summary = summary.sort_values(
    ["avg_points", "matches"],
    ascending=[False, False]
)

# ------------------------
# SAVE
# ------------------------
summary.to_csv(
    "data/processed/ol_lineup_impact.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_lineup_impact.csv")
print("=== STEP 3 TERMINÉ ===")
