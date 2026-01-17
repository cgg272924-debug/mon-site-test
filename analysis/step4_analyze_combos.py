import pandas as pd

print("=== STEP 4 — ANALYSE FINALE DES COMBOS ===")

df = pd.read_csv("data/processed/ol_combos_with_results.csv")

print("Colonnes :", df.columns.tolist())
print("Lignes :", df.shape[0])

# Agrégation finale
summary = (
    df.groupby(["combo", "size"])
    .agg(
        matches=("match_key", "nunique"),
        avg_points=("points", "mean"),
        avg_score=("score_final", "mean")
    )
    .reset_index()
)

# Arrondis
summary["avg_points"] = summary["avg_points"].round(2)
summary["avg_score"] = summary["avg_score"].round(2)

# Filtre minimum de matchs (important)
summary = summary[summary["matches"] >= 3]

summary = summary.sort_values(
    ["avg_points", "avg_score", "matches"],
    ascending=False
)

summary.to_csv(
    "data/processed/ol_combo_impact_final.csv",
    index=False
)

print("📁 Fichier créé : data/processed/ol_combo_impact_final.csv")
print("Combinaisons retenues :", summary.shape[0])
print("=== STEP 4 TERMINÉ ===")
