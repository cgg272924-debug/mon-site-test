import pandas as pd

print("=== STEP 3 — COMBOS AVEC RESULTATS ===")

df = pd.read_csv("data/processed/ol_combos_per_match.csv")

print("Combos par match chargés :", df.shape)

cols = [c for c in ["match_key", "combo", "size", "points", "score_final"] if c in df.columns]
out = df[cols].copy()

out.to_csv(
    "data/processed/ol_combos_with_results.csv",
    index=False,
)

print("📁 Fichier créé : data/processed/ol_combos_with_results.csv")
print("Lignes écrites :", out.shape[0])
print("=== STEP 3 TERMINÉ ===")
