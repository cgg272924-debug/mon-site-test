import pandas as pd

print("=== ETAPE 2 — IMPACT DES COMBINAISONS ===")

# =====================
# CHARGEMENT
# =====================

df = pd.read_csv("data/processed/ol_lineups_with_results.csv")

print("Colonnes :", list(df.columns))
print("Lignes :", df.shape[0])

# =====================
# AGRÉGATION
# =====================

summary = (
    df.groupby(["combo", "size"])
    .agg(
        matches=("points", "count"),
        avg_points=("points", "mean"),
        avg_score=("score_final", "mean")
    )
    .reset_index()
)

# =====================
# FILTRE MINIMUM DE MATCHS
# =====================

summary = summary[summary["matches"] >= 3]

# =====================
# TRI PAR PERFORMANCE
# =====================

summary = summary.sort_values(
    by=["avg_points", "avg_score", "matches"],
    ascending=False
)

# =====================
# SAUVEGARDE
# =====================

output = "data/processed/ol_lineup_impact_summary.csv"
summary.to_csv(output, index=False)

print("Combinaisons retenues :", summary.shape[0])
print(f"📁 Fichier créé : {output}")
print("=== ETAPE 2 TERMINÉE ===")
