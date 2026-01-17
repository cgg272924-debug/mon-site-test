import pandas as pd
from pathlib import Path

print("=== CALCUL SCORE FINAL MATCH OL ===")

# Paths
CLEAN_PATH = Path("data/processed/ol_matches_clean.csv")
RATED_PATH = Path("data/processed/ol_matches_rated.csv")
OUTPUT_PATH = Path("data/processed/ol_match_score_final.csv")

# Load data
df_clean = pd.read_csv(CLEAN_PATH)
df_rated = pd.read_csv(RATED_PATH)

# Debug colonnes
print("Colonnes clean :", df_clean.columns.tolist())
print("Colonnes rated :", df_rated.columns.tolist())

# 👉 On merge sur date + opponent + venue (clé fiable)
df = df_clean.merge(
    df_rated[["date", "opponent", "venue", "match_rating"]],
    on=["date", "opponent", "venue"],
    how="left"
)

# Points by result
def result_to_points(result):
    if result == "W":
        return 3
    elif result == "D":
        return 1
    else:
        return 0

df["points"] = df["result"].apply(result_to_points)

# Score final (mix résultat + perf)
df["score_final"] = (df["points"] / 3) * 40 + df["match_rating"] * 0.60
df["score_final"] = df["score_final"].round(2)

# Colonnes finales
df_final = df[[
    "date",
    "opponent",
    "venue",
    "result",
    "points",
    "match_rating",
    "score_final"
]]

# Save
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(OUTPUT_PATH, index=False)

print(f"Matchs traités : {len(df_final)}")
print(f"📁 Fichier créé : {OUTPUT_PATH}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
