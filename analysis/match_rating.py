import pandas as pd
import os

print("=== NOTATION DES MATCHS OL ===")

# Chemins
INPUT_PATH = "data/processed/ol_matches_clean.csv"
OUTPUT_PATH = "data/processed/ol_matches_rated.csv"

# Vérification fichier
if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError("Fichier ol_matches_clean.csv introuvable")

# Chargement
df = pd.read_csv(INPUT_PATH)

# Fonction de notation d’un match
def rate_match(row):
    score = 50  # base neutre

    # Résultat
    if row["result"] == "W":
        score += 20
    elif row["result"] == "D":
        score += 5
    elif row["result"] == "L":
        score -= 15

    # xG différence
    if not pd.isna(row["xG"]) and not pd.isna(row["xGA"]):
        xg_diff = row["xG"] - row["xGA"]
        score += xg_diff * 10

    # Réalisme offensif
    score += (row["GF"] - row["xG"]) * 5 if not pd.isna(row["xG"]) else 0

    # Solidité défensive
    score += (row["xGA"] - row["GA"]) * 5 if not pd.isna(row["xGA"]) else 0

    # Domicile / extérieur
    if row["venue"] == "Away":
        score += 3  # bonus extérieur

    # Bornes
    score = max(0, min(100, round(score, 1)))

    return score

# Application
df["match_rating"] = df.apply(rate_match, axis=1)

# Sauvegarde
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

print(f"Matchs notés : {len(df)}")
print(f"Fichier créé : {OUTPUT_PATH}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
