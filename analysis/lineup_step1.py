import pandas as pd

print("=== STEP 1 — CREATION LINEUPS PAR MATCH ===")

# ------------------------
# LOAD DATA
# ------------------------
players = pd.read_csv("data/processed/ol_player_minutes.csv")
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

print("Joueurs chargés :", players.shape)
print("Matchs chargés  :", matches.shape)

# ------------------------
# CLEAN PLAYERS
# ------------------------
players = players.rename(columns={
    "min": "minutes_played"
})

players["minutes_played"] = pd.to_numeric(players["minutes_played"], errors="coerce")
players = players[players["minutes_played"] >= 30]

# ------------------------
# CREATE MATCH KEY
# ------------------------
matches["match_key"] = (
    matches["date"].astype(str) + "_" +
    matches["opponent"].astype(str)
)

players["match_key"] = (
    players["season"].astype(str) + "_" +
    players["game"].astype(str)
)

# ------------------------
# KEEP USEFUL COLUMNS
# ------------------------
players = players[[
    "match_key",
    "player",
    "pos",
    "minutes_played"
]]

# ------------------------
# SAVE
# ------------------------
players.to_csv(
    "data/processed/ol_lineups_by_match.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_lineups_by_match.csv")
print("Lignes :", len(players))
print("=== STEP 1 TERMINÉ ===")
