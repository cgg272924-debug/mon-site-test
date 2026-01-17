import pandas as pd
from pathlib import Path

print("=== IDENTIFICATION JOUEURS CLES OL (TOP GLOBAL + COMPOSANTS) ===")

PLAYERS_PATH = Path("data/processed/ol_players_rated.csv")
OUTPUT_PATH = Path("data/processed/ol_key_players.csv")

df = pd.read_csv(PLAYERS_PATH)

def normalize(series):
    s = series.fillna(0)
    rng = s.max() - s.min()
    if rng == 0:
        return s * 0
    return (s - s.min()) / rng

df["minutes_n"] = normalize(df["Playing Time_Min"])
df["rating_n"] = normalize(df["rating"])

df["importance"] = (
    df["rating_n"] * 0.65 +
    df["minutes_n"] * 0.35
) * 100

cols_components = [
    "Per 90 Minutes_Gls",
    "Per 90 Minutes_Ast",
    "Per 90 Minutes_xG",
    "Per 90 Minutes_xAG",
    "Progression_PrgC",
    "Progression_PrgP",
    "Progression_PrgR",
    "Performance_CrdY",
    "Performance_CrdR",
]
for c in cols_components:
    if c not in df.columns:
        df[c] = 0

df_sorted = df.sort_values("importance", ascending=False).copy()

gk_mask = df_sorted["pos"].astype(str).str.upper() == "GK"
df_gk = df_sorted[gk_mask].copy()
df_field = df_sorted[~gk_mask].copy()

top_field = df_field.head(10)
top_gk = df_gk.head(2)

key_players = pd.concat([top_field, top_gk], ignore_index=True)

key_players = key_players[[
    "player",
    "pos",
    "Playing Time_Min",
    "rating",
    "importance",
    "Per 90 Minutes_Gls",
    "Per 90 Minutes_Ast",
    "Per 90 Minutes_xG",
    "Per 90 Minutes_xAG",
    "Progression_PrgC",
    "Progression_PrgP",
    "Progression_PrgR",
    "Performance_CrdY",
    "Performance_CrdR",
]].drop_duplicates(subset="player")

key_players = key_players.sort_values("importance", ascending=False)

key_players.to_csv(OUTPUT_PATH, index=False)

print(f"Joueurs clés identifiés : {len(key_players)}")
print(key_players[["player", "pos", "importance"]])
print(f"Fichier créé : {OUTPUT_PATH}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
