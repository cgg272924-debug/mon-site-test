import pandas as pd
from itertools import combinations

print("=== ANALYSE COMBINAISONS DE JOUEURS (LINEUPS) – V1 ===")

# --- Chargement ---
df = pd.read_csv("data/processed/ol_player_minutes.csv")

print("Colonnes disponibles :", list(df.columns))

# --- Sécurité colonne minutes ---
if "minutes_played" not in df.columns:
    raise ValueError("❌ Colonne 'minutes_played' absente")

# --- Filtre joueurs réellement impliqués ---
df = df[df["minutes_played"] >= 60]

# --- Construction des lineups par match ---
lineups = (
    df.groupby("game")["player"]
    .apply(lambda x: sorted(set(x)))
    .reset_index()
)

print(f"Matchs analysés : {len(lineups)}")

# --- Proxy points match (temporaire mais cohérent) ---
lineups["points"] = 1.41  # moyenne OL actuelle

# --- Génération des combinaisons ---
records = []

for _, row in lineups.iterrows():
    players = row["player"]
    points = row["points"]

    for r in [2, 3, 4]:
        for combo in combinations(players, r):
            records.append({
                "combo": " + ".join(combo),
                "size": r,
                "points": points
            })

df_combo = pd.DataFrame(records)

# --- Agrégation ---
summary = (
    df_combo
    .groupby(["combo", "size"])
    .agg(
        matches=("points", "count"),
        avg_points=("points", "mean")
    )
    .reset_index()
)

# --- Filtrage combos significatives ---
summary = summary[summary["matches"] >= 3]
summary = summary.sort_values("avg_points", ascending=False)

# --- Sauvegarde ---
summary.to_csv("data/processed/ol_lineup_impact.csv", index=False)

print(f"Combinaisons retenues : {len(summary)}")
print("📁 Fichier créé : data/processed/ol_lineup_impact.csv")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
