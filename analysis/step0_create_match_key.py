import pandas as pd

print("=== STEP 0 — CREATION MATCH_KEY (FIX DATE GAME) ===")

# ===== MATCHES =====
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

matches["date"] = pd.to_datetime(matches["date"], errors="coerce").dt.date
matches["opponent"] = matches["opponent"].str.lower().str.strip()

matches["match_key"] = matches["date"].astype(str) + "_" + matches["opponent"]

matches_out = matches[[
    "match_key", "date", "opponent", "venue",
    "result", "points", "match_rating", "score_final"
]]

matches_out.to_csv(
    "data/processed/ol_matches_with_match_key.csv",
    index=False
)

print("✅ Matchs traités :", matches_out.shape)


# ===== PLAYERS =====
players = pd.read_csv("data/processed/ol_player_minutes.csv")

players["season"] = pd.to_numeric(players["season"], errors="coerce")
current_season = players["season"].max()
players = players[players["season"] == current_season]

players["game_date"] = players["game"].astype(str).str[:10]
players["game_date"] = pd.to_datetime(players["game_date"], errors="coerce").dt.date

players["team"] = players["team"].str.lower().str.strip()

players["match_key"] = players["game_date"].astype(str) + "_" + players["team"]

players_out = players[[
    "match_key", "player", "pos", "age",
    "minutes_played", "goals", "assists", "xg", "xag"
]]

players_out.to_csv(
    "data/processed/ol_players_with_match_key.csv",
    index=False
)

print("✅ Joueurs traités :", players_out.shape)
print("=== STEP 0 TERMINÉ AVEC SUCCÈS ===")
