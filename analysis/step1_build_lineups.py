import pandas as pd

print("=== STEP 1 — CONSTRUCTION DES LINEUPS ===")

players = pd.read_csv("data/processed/ol_players_with_match_key.csv")

print("Joueurs chargés :", players.shape)

players = players[players["minutes_played"] > 0]

cols_lineups_by_match = [
    "match_key",
    "player",
    "pos",
    "age",
    "minutes_played",
    "goals",
    "assists",
    "xg",
    "xag",
]
existing_cols = [c for c in cols_lineups_by_match if c in players.columns]

lineups_long = players[existing_cols].copy()

lineups_long.to_csv(
    "data/processed/ol_lineups_by_match.csv",
    index=False,
)

print("Lineups par match créées :", lineups_long.shape)
print("📁 Fichier créé : data/processed/ol_lineups_by_match.csv")

agg = (
    lineups_long.groupby("match_key")["player"]
    .apply(lambda x: sorted(set(x)))
    .reset_index()
)
agg["size"] = agg["player"].apply(len)
agg = agg.rename(columns={"player": "players"})

agg.to_csv(
    "data/processed/ol_match_lineups.csv",
    index=False,
)

print("Lineups agrégées créées :", agg.shape)
print("📁 Fichier créé : data/processed/ol_match_lineups.csv")
print("=== STEP 1 TERMINÉ ===")
