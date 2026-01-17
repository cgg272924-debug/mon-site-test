import pandas as pd
import numpy as np

print("=== NOTATION JOUEURS OL (SUR 100) ===")

# Chargement des stats joueurs
df = pd.read_csv("data/raw/ol_players_stats_raw.csv")

# Sécurité : remplacer NaN par 0
df = df.fillna(0)

# Filtrer joueurs avec au moins 300 minutes
df = df[df["Playing Time_Min"] >= 300]

# -----------------------------
# NORMALISATION (0 → 1)
# -----------------------------
def normalize(col):
    if col.max() == col.min():
        return 0
    return (col - col.min()) / (col.max() - col.min())

df["gls_n"] = normalize(df["Per 90 Minutes_Gls"])
df["ast_n"] = normalize(df["Per 90 Minutes_Ast"])
df["xg_n"] = normalize(df["Per 90 Minutes_xG"])
df["xag_n"] = normalize(df["Per 90 Minutes_xAG"])

df["prgc_n"] = normalize(df["Progression_PrgC"])
df["prgp_n"] = normalize(df["Progression_PrgP"])
df["prgr_n"] = normalize(df["Progression_PrgR"])

# Discipline (inversée)
df["disc_n"] = 1 - normalize(df["Performance_CrdY"] + df["Performance_CrdR"])

# -----------------------------
# SCORE FINAL
# -----------------------------
df["rating"] = (
    df["gls_n"] * 25 +
    df["ast_n"] * 15 +
    df["xg_n"] * 15 +
    df["xag_n"] * 10 +
    df["prgc_n"] * 10 +
    df["prgp_n"] * 10 +
    df["prgr_n"] * 10 +
    df["disc_n"] * 5
)

# Arrondi
df["rating"] = df["rating"].round(1)

# Trier par note
df = df.sort_values("rating", ascending=False)

# Sauvegarde
df.to_csv("data/processed/ol_players_rated.csv", index=False)

print(f"Joueurs notés : {len(df)}")
print("Fichier créé : data/processed/ol_players_rated.csv")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
