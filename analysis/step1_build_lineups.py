import pandas as pd

print("=== STEP 1 — CONSTRUCTION DES LINEUPS ===")

players = pd.read_csv("data/processed/ol_players_with_match_key.csv")

print("Joueurs chargés :", players.shape)

# On garde uniquement les joueurs ayant joué
players = players[players["minutes_played"] > 0]

# Construction lineup par match
lineups = (
    players
    .groupby("match_key")["player"]
    .apply(lambda x: sorted(set(x)))
    .reset_index()
)

lineups["size"] = lineups["player"].apply(len)
lineups.rename(columns={"player": "players"}, inplace=True)

lineups.to_csv(
    "data/processed/ol_match_lineups.csv",
    index=False
)

print("Lineups créées :", lineups.shape)
print("📁 Fichier créé : data/processed/ol_match_lineups.csv")
print("=== STEP 1 TERMINÉ ===")
