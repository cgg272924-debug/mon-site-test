import pandas as pd
import itertools

print("=== ANALYSE LINEUPS → SCORE FINAL (V2 STABLE) ===")

# =========================
# LOAD DATA
# =========================
players_path = "data/processed/ol_player_minutes.csv"
scores_path = "data/processed/ol_match_score_final.csv"

df_players = pd.read_csv(players_path)
df_scores = pd.read_csv(scores_path)

print("Colonnes joueurs :", df_players.columns.tolist())
print("Colonnes scores :", df_scores.columns.tolist())

# =========================
# NORMALISATION
# =========================
# Minutes jouées
if "min" in df_players.columns:
    df_players["minutes_played"] = pd.to_numeric(df_players["min"], errors="coerce")
elif "minutes_played" not in df_players.columns:
    raise ValueError("Aucune colonne minutes trouvée")

df_players = df_players.dropna(subset=["minutes_played"])

# On garde les joueurs réellement impliqués
df_players = df_players[df_players["minutes_played"] >= 60]

# Normalisation game_id
df_players["game_id"] = df_players["game_id"].astype(str)
df_scores["game_id"] = df_scores.index.astype(str)

# =========================
# MERGE JOUEURS ↔ MATCHS
# =========================
df = df_players.merge(
    df_scores[["game_id", "score_final"]],
    on="game_id",
    how="inner"
)

print("Lignes après merge :", len(df))

if df.empty:
    print("❌ Merge vide → aucun match commun")
    exit()

# =========================
# CONSTRUCTION LINEUPS
# =========================
records = []

for game_id, g in df.groupby("game_id"):
    players = sorted(g["player"].unique())
    score = g["score_final"].iloc[0]

    # combos de 2 à 5 joueurs
    for size in range(2, min(6, len(players) + 1)):
        for combo in itertools.combinations(players, size):
            records.append({
                "combo": " + ".join(combo),
                "size": size,
                "score": score
            })

combo_df = pd.DataFrame(records)

if combo_df.empty:
    print("❌ Aucune combinaison générée")
    print("➡️ Causes possibles :")
    print("- Pas assez de joueurs ≥ 60 min")
    print("- game_id non alignés")
    exit()

# =========================
# AGGREGATION
# =========================
final = (
    combo_df
    .groupby(["combo", "size"])
    .agg(
        matches=("score", "count"),
        avg_score=("score", "mean")
    )
    .reset_index()
    .sort_values(["avg_score", "matches"], ascending=False)
)

# =========================
# SAVE
# =========================
output_path = "data/processed/ol_lineup_score_impact.csv"
final.to_csv(output_path, index=False)

print(f"📁 Fichier créé : {output_path}")
print("Combinaisons analysées :", len(final))
print("=== SCRIPT TERMINÉ AVEC SUCCÈS ===")
