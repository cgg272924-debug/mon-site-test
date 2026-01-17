import pandas as pd

print("=== ETAPE 1 FIX — CREATION CLE MATCH ===")

# =====================
# MATCHS
# =====================

matches = pd.read_csv("data/processed/ol_match_score_final.csv")

matches["match_key"] = (
    matches["date"].astype(str)
    + "_"
    + matches["opponent"].astype(str)
)

matches = matches[[
    "match_key",
    "date",
    "opponent",
    "points",
    "score_final"
]]

print("Matchs :", matches.shape)

# =====================
# JOUEURS
# =====================

players = pd.read_csv("data/processed/ol_player_minutes.csv")

players["match_key"] = (
    players["game"].astype(str)
)

players = players[[
    "match_key",
    "player"
]]

print("Joueurs :", players.shape)

# =====================
# COMBOS PAR MATCH
# =====================

combos = (
    players.groupby("match_key")["player"]
    .apply(lambda x: " + ".join(sorted(x)))
    .reset_index()
)

combos["size"] = combos["player"].apply(lambda x: len(x.split(" + ")))
combos = combos.rename(columns={"player": "combo"})

print("Combos :", combos.shape)

# =====================
# MERGE FINAL
# =====================

df = combos.merge(matches, on="match_key", how="inner")

print("Lignes finales :", df.shape)

# =====================
# SAUVEGARDE
# =====================

output = "data/processed/ol_lineups_with_results.csv"
df.to_csv(output, index=False)

print(f"📁 Fichier créé : {output}")
print("=== ETAPE 1 FIX TERMINÉE ===")
