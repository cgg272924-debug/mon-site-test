import pandas as pd

print("=== STEP 3 — MERGE COMBOS + RESULTATS MATCHS ===")

combos = pd.read_csv("data/processed/ol_lineup_cooccurrence.csv")
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

print("Combos :", combos.shape)
print("Matchs :", matches.shape)

# On renomme proprement
matches = matches.reset_index().rename(columns={"index": "match_id"})

# On suppose que les lignes de combos ont un game_id
df = combos.merge(
    matches,
    left_on="game_id",
    right_on="match_id",
    how="inner"
)

print("Lignes après merge :", df.shape[0])

df = df[[
    "game_id",
    "combo",
    "size",
    "points",
    "score_final"
]]

df.to_csv(
    "data/processed/ol_combos_with_results.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_combos_with_results.csv")
print("=== STEP 3 TERMINÉ ===")
