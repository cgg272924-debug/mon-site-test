import pandas as pd

print("=== ETAPE 1 FIX — CREATION LINEUPS AVEC RESULTATS (XI TITULAIRES) ===")

lineups = pd.read_csv("data/processed/ol_lineups_by_match.csv")
matches = pd.read_csv("data/processed/ol_matches_with_match_key.csv")

print("Lineups :", lineups.shape)
print("Matchs :", matches.shape)

if "is_starter" in lineups.columns:
    lineups = lineups[lineups["is_starter"]]

lineup_combos = (
    lineups.groupby("match_key")["player"]
    .apply(lambda x: " + ".join(sorted(x.dropna().unique())))
    .reset_index()
)

lineup_combos["size"] = lineup_combos["player"].apply(lambda v: len(v.split(" + ")))
lineup_combos = lineup_combos.rename(columns={"player": "combo"})

matches_subset = matches[["match_key", "date", "opponent", "points", "score_final"]]

df = lineup_combos.merge(matches_subset, on="match_key", how="inner")

print("Lignes finales :", df.shape)

output = "data/processed/ol_lineups_with_results.csv"
df.to_csv(output, index=False)

print(f"Fichier créé : {output}")
print("=== ETAPE 1 FIX TERMINÉE ===")
