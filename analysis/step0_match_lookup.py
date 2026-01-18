import pandas as pd
import os

print("=== STEP 0 — CREATION match_lookup.csv ===")

# Charger les scores de match
df = pd.read_csv("data/processed/ol_match_score_final.csv")

print("Colonnes source :", df.columns.tolist())
print("Matchs trouvés :", len(df))

# Création clé match simple et stable
df["match_key"] = (
    df["date"].astype(str)
    + "_" +
    df["opponent"].astype(str)
)

# Sélection des colonnes utiles
lookup = df[[
    "match_key",
    "date",
    "opponent",
    "venue",
    "points",
    "score_final"
]].copy()

# Ajouter colonnes futures (vides pour l’instant)
lookup["season"] = ""
lookup["game_id"] = ""

# Réorganisation propre
lookup = lookup[
    ["match_key", "season", "game_id", "date", "opponent", "venue", "points", "score_final"]
]

# Création dossier si besoin
os.makedirs("data/processed", exist_ok=True)

# Sauvegarde
output_path = "data/processed/match_lookup.csv"
lookup.to_csv(output_path, index=False)

print(f"Fichier créé : {output_path}")
print("Lignes :", len(lookup))
print("=== STEP 0 TERMINÉE ===")
