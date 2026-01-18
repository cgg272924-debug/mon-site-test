import pandas as pd
from pathlib import Path

print("=== IDENTIFICATION JOUEURS CLES OL (TOP GLOBAL + COMPOSANTS) ===")

PLAYERS_PATH = Path("data/processed/ol_players_rated.csv")
MINUTES_PATH = Path("data/processed/ol_player_minutes.csv")
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
key_players = df_sorted.copy()

if MINUTES_PATH.exists():
    minutes_df = pd.read_csv(MINUTES_PATH)
    if "minutes_played" in minutes_df.columns:
        minutes_df["minutes_played"] = pd.to_numeric(
            minutes_df["minutes_played"], errors="coerce"
        ).fillna(0)
        agg = (
            minutes_df.groupby(["player", "pos"])["minutes_played"]
            .sum()
            .reset_index()
        )
        agg = agg.sort_values(
            ["player", "minutes_played"], ascending=[True, False]
        )
        primary = agg.drop_duplicates("player")
        primary_map = dict(zip(primary["player"], primary["pos"]))
        key_players["primary_pos_en"] = key_players["player"].map(primary_map)
    else:
        key_players["primary_pos_en"] = key_players["pos"].astype(str)
else:
    key_players["primary_pos_en"] = key_players["pos"].astype(str)

POSITION_EN_TO_FR = {
    "GK": "G",
    "DF": "DC",
    "CB": "DC",
    "LB": "DG",
    "LWB": "DG",
    "RB": "DD",
    "RWB": "DD",
    "WB": "DG",
    "DM": "MDC",
    "CDM": "MDC",
    "MF": "MC",
    "CM": "MC",
    "AM": "MOC",
    "CAM": "MOC",
    "LM": "MG",
    "RM": "MD",
    "LW": "AG",
    "RW": "AD",
    "FW": "BU",
    "ST": "BU",
}

def map_en_to_fr(pos: str) -> str:
    p = str(pos or "").upper()
    primary = p.split(",")[0].strip()
    if not primary:
        return "-"
    return POSITION_EN_TO_FR.get(primary, primary)

key_players["pos_fr"] = key_players["primary_pos_en"].apply(map_en_to_fr)

key_players = key_players[[
    "player",
    "primary_pos_en",
    "pos_fr",
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

key_players = key_players.rename(columns={"primary_pos_en": "pos"})

key_players.to_csv(OUTPUT_PATH, index=False)

print(f"Joueurs clés identifiés : {len(key_players)}")
print(key_players[["player", "pos", "pos_fr", "importance"]])
print(f"Fichier créé : {OUTPUT_PATH}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
