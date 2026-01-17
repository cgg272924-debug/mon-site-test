import pandas as pd
from itertools import combinations

print("=== ETAPE 1 — LINEUPS + MATCH RESULT (CORRIGÉ) ===")

# =====================
# CHARGEMENT DES DONNÉES
# =====================

players = pd.read_csv("data/processed/ol_player_minutes.csv")
matches = pd.read_csv("data/processed/ol_match_score_final.csv")

print("Colonnes joueurs :", list(players.columns))
print("Colonnes matchs  :", list(matches.columns))

# =====================
# FILTRE TEMPS DE JEU
# =====================

players["minutes_played"] = pd.to_numeric(players["minutes_played"], errors="coerce")
players = players[players["minutes_played"] >= 60]

print("Joueurs après filtre 60 min :", players.shape)

# =====================
# CLÉ MATCH SIMPLE
# =====================

players["match_key"] = (
    players["season"].astype(str) + "_" +
    players["game"].astype(str)
)

matches["match_key"] = (
    matches["date"].astype(str) + "_" +
    matches["opponent"].astype(str) + "_" +
    matches["venue"].astype(str)
)

# =====================
# LINEUPS PAR MATCH
# =====================

lineups = []

for match, df_match in players.groupby("match_key"):
    joueurs = sorted(df_match["player"].unique())

    for size in range(2, 6):  # combos 2 → 5
        for combo in combinations(joueurs, size):
            lineups.append({
                "match_key": match,
                "combo": " + ".join(combo),
                "size": size
            })

df_lineups = pd.DataFrame(lineups)

print("Combinaisons générées :", len(df_lineups))

# =====================
# MERGE AVEC RÉSULTATS
# =====================

df_final = df_lineups.merge(
    matches[["match_key", "points", "score_final"]],
    on="match_key",
    how="inner"
)

print("Lignes finales après merge :", len(df_final))

# =====================
# SAUVEGARDE
# =====================

output = "data/processed/ol_lineups_with_results.csv"
df_final.to_csv(output, index=False)

print(f"📁 Fichier créé : {output}")
print("=== ETAPE 1 TERMINÉE ===")
