import pandas as pd
import os

RAW_PATH = "data/raw/ligue1_matches_raw.csv"
OUT_PATH = "data/processed/ol_matches_clean.csv"

print("=== NETTOYAGE MATCHS OL ===")

# Lecture du fichier brut
df = pd.read_csv(RAW_PATH)

# Filtrage des matchs où Lyon est impliqué
df_ol = df[
    df["match_report"].str.contains("Lyon", case=False, na=False)
]

print(f"Matchs OL trouvés : {len(df_ol)}")

# Colonnes utiles pour l'analyse
df_ol = df_ol[[
    "date",
    "venue",
    "opponent",
    "result",
    "GF",
    "GA",
    "xG",
    "xGA",
    "Poss",
    "Formation",
    "Opp Formation"
]]

# Nettoyage des types
df_ol["date"] = pd.to_datetime(df_ol["date"], errors="coerce")
df_ol["GF"] = pd.to_numeric(df_ol["GF"], errors="coerce")
df_ol["GA"] = pd.to_numeric(df_ol["GA"], errors="coerce")
df_ol["xG"] = pd.to_numeric(df_ol["xG"], errors="coerce")
df_ol["xGA"] = pd.to_numeric(df_ol["xGA"], errors="coerce")

df_ol["Poss"] = (
    df_ol["Poss"]
    .astype(str)
    .str.replace("%", "", regex=False)
)

df_ol["Poss"] = pd.to_numeric(df_ol["Poss"], errors="coerce")

# Création du dossier processed si absent
os.makedirs("data/processed", exist_ok=True)

# Sauvegarde
df_ol.to_csv(OUT_PATH, index=False, encoding="utf-8")

print("Fichier créé :", OUT_PATH)
print("=== SCRIPT TERMINE AVEC SUCCES ===")
