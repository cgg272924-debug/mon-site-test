import pandas as pd
import numpy as np

print("=== NOTATION JOUEURS OL (SUR 100) ===")

# Chargement des stats joueurs
df = pd.read_csv("data/raw/ol_players_stats_raw.csv")

# Sécurité : remplacer NaN par 0
df = df.fillna(0)

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

df["disc_n"] = 1 - normalize(df["Performance_CrdY"] + df["Performance_CrdR"])
df["minutes_n"] = normalize(df["Playing Time_Min"])

def compute_role_weights(pos: str) -> dict:
    p = (pos or "").upper()
    is_gk = "GK" in p
    is_def = any(tag in p for tag in ["DF", "CB", "LB", "RB"])
    is_mid = any(tag in p for tag in ["MF", "DM", "CM"])
    is_fw = "FW" in p or "ST" in p

    if is_gk:
        return {
            "gls": 2,
            "ast": 2,
            "xg": 3,
            "xag": 3,
            "prgc": 15,
            "prgp": 15,
            "prgr": 15,
            "disc": 5,
            "minutes": 20,
        }
    if is_def:
        return {
            "gls": 5,
            "ast": 5,
            "xg": 5,
            "xag": 5,
            "prgc": 25,
            "prgp": 20,
            "prgr": 20,
            "disc": 15,
            "minutes": 15,
        }
    if is_mid:
        return {
            "gls": 10,
            "ast": 15,
            "xg": 15,
            "xag": 15,
            "prgc": 15,
            "prgp": 15,
            "prgr": 10,
            "disc": 5,
            "minutes": 10,
        }
    return {
        "gls": 25,
        "ast": 15,
        "xg": 15,
        "xag": 10,
        "prgc": 10,
        "prgp": 10,
        "prgr": 10,
        "disc": 5,
        "minutes": 5,
    }

weights = df["pos"].astype(str).apply(compute_role_weights)

df["rating"] = (
    df["gls_n"] * weights.apply(lambda w: w["gls"]) +
    df["ast_n"] * weights.apply(lambda w: w["ast"]) +
    df["xg_n"] * weights.apply(lambda w: w["xg"]) +
    df["xag_n"] * weights.apply(lambda w: w["xag"]) +
    df["prgc_n"] * weights.apply(lambda w: w["prgc"]) +
    df["prgp_n"] * weights.apply(lambda w: w["prgp"]) +
    df["prgr_n"] * weights.apply(lambda w: w["prgr"]) +
    df["disc_n"] * weights.apply(lambda w: w["disc"]) +
    df["minutes_n"] * weights.apply(lambda w: w["minutes"])
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
