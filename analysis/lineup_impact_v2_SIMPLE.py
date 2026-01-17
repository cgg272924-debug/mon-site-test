import pandas as pd
import itertools

print("=== ANALYSE LINEUPS OL — CO-OCCURRENCE ===")

# =========================
# LOAD
# =========================
df = pd.read_csv("data/processed/ol_player_minutes.csv")

print("Colonnes :", df.columns.tolist())

# =========================
# FILTRES
# =========================
df["minutes_played"] = pd.to_numeric(df["minutes_played"], errors="coerce")
df = df[df["minutes_played"] >= 60]

df["game_id"] = df["game_id"].astype(str)

# =========================
# COMBINAISONS
# =========================
records = []

for game_id, g in df.groupby("game_id"):
    players = sorted(g["player"].unique())

    for size in range(2, min(6, len(players) + 1)):
        for combo in itertools.combinations(players, size):
            records.append({
                "combo": " + ".join(combo),
                "size": size
            })

combo_df = pd.DataFrame(records)

# =========================
# AGGREGATION
# =========================
final = (
    combo_df
    .groupby(["combo", "size"])
    .size()
    .reset_index(name="matches_together")
    .sort_values("matches_together", ascending=False)
)

# =========================
# SAVE
# =========================
final.to_csv("data/processed/ol_lineup_cooccurrence.csv", index=False)

print("📁 Fichier créé : data/processed/ol_lineup_cooccurrence.csv")
print("Combinaisons trouvées :", len(final))
print("=== TERMINÉ ===")
