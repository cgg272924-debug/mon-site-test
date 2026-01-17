import pandas as pd
from pathlib import Path

print("=== IDENTIFICATION JOUEURS CLÉS OL (POSTE-AWARE + GK) ===")

# Paths
PLAYERS_PATH = Path("data/processed/ol_players_rated.csv")
OUTPUT_PATH = Path("data/processed/ol_key_players.csv")

# Load data
df = pd.read_csv(PLAYERS_PATH)

# -----------------------------
# NORMALISATION PAR POSTE
# -----------------------------
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

df["minutes_n"] = normalize(df["Playing Time_Min"].fillna(0))
df["rating_n"] = normalize(df["rating"].fillna(0))

# Importance score (joueurs de champ)
df["importance"] = (
    df["rating_n"] * 0.6 +
    df["minutes_n"] * 0.4
) * 100

# -----------------------------
# JOUEURS CLÉS PAR POSTE (hors GK)
# -----------------------------
key_players = []

for pos in ["DF", "MF", "FW"]:
    subset = df[df["pos"].str.contains(pos, na=False)]
    if not subset.empty:
        top_player = subset.sort_values("importance", ascending=False).iloc[0]
        key_players.append(top_player)

key_players = pd.DataFrame(key_players)

# -----------------------------
# AJOUT GARDIEN TITULAIRE (LOGIQUE MÉTIER)
# -----------------------------
gk = df[df["pos"] == "GK"].sort_values("Playing Time_Min", ascending=False)

if not gk.empty:
    main_gk = gk.iloc[0]
    gk_row = {
        "player": main_gk["player"],
        "pos": "GK",
        "Playing Time_Min": main_gk["Playing Time_Min"],
        "rating": main_gk["rating"],
        "importance": 75.0  # valeur métier élevée
    }
    key_players = pd.concat(
        [key_players, pd.DataFrame([gk_row])],
        ignore_index=True
    )

# -----------------------------
# NETTOYAGE & EXPORT
# -----------------------------
key_players = key_players[[
    "player",
    "pos",
    "Playing Time_Min",
    "rating",
    "importance"
]].drop_duplicates(subset="player")

key_players = key_players.sort_values("importance", ascending=False)

key_players.to_csv(OUTPUT_PATH, index=False)

print(f"Joueurs clés identifiés : {len(key_players)}")
print(key_players[["player", "pos", "importance"]])
print(f"Fichier créé : {OUTPUT_PATH}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
