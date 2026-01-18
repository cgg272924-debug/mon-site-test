import pandas as pd

print("=== ANALYSE LINEUPS OL — CO-OCCURRENCE ===")

df = pd.read_csv("data/processed/ol_combos_per_match.csv")

print("Combos par match chargés :", df.shape)

if "match_key" in df.columns:
    grp = df.groupby(["combo", "size"])["match_key"].nunique()
else:
    grp = df.groupby(["combo", "size"]).size()

final = (
    grp.reset_index(name="matches_together")
    .sort_values("matches_together", ascending=False)
)

final.to_csv("data/processed/ol_lineup_cooccurrence.csv", index=False)

print("📁 Fichier créé : data/processed/ol_lineup_cooccurrence.csv")
print("Combinaisons trouvées :", len(final))
print("=== TERMINÉ ===")
