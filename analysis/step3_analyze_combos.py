import pandas as pd

print("=== STEP 3 — ANALYSE DES COMBOS ===")

df = pd.read_csv("data/processed/ol_combos_per_match.csv")

print("Lignes chargées :", df.shape)

summary = (
    df
    .groupby(["combo", "size"])
    .agg(
        matches=("points", "count"),
        avg_points=("points", "mean"),
        avg_score_final=("score_final", "mean")
    )
    .reset_index()
)

# Filtre anti-bruit
summary = summary[summary["matches"] >= 3]

# Arrondis
summary["avg_points"] = summary["avg_points"].round(2)
summary["avg_score_final"] = summary["avg_score_final"].round(2)

print("Combos retenus :", summary.shape)

summary.to_csv(
    "data/processed/ol_combo_impact_summary.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_combo_impact_summary.csv")
print("=== STEP 3 TERMINÉ ===")
