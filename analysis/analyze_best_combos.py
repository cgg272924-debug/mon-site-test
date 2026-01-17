import pandas as pd
from pathlib import Path

print("=== ANALYSE — COMBINAISONS OL (3 À 11 JOUEURS) ===")

# =========================
# 1. Chargement
# =========================
input_path = "data/processed/ol_combo_impact_summary.csv"
df = pd.read_csv(input_path)

print(f"Lignes totales : {len(df)}")
print("Colonnes disponibles :", df.columns.tolist())

# =========================
# 2. Nettoyage types
# =========================
numeric_cols = ["matches", "avg_points", "avg_score_final", "size"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 3. Dossier de sortie
# =========================
output_dir = Path("data/processed/best_combos_by_size")
output_dir.mkdir(parents=True, exist_ok=True)

all_results = []

# =========================
# 4. Boucle tailles 3 → 11
# =========================
for size in range(3, 12):
    subset = df[
        (df["size"] == size) &
        (df["matches"] >= 3)
    ].copy()

    if subset.empty:
        print(f"⏭️  Taille {size} — aucun combo valide")
        continue

    subset = subset.sort_values(
        by=["avg_points", "avg_score_final"],
        ascending=False
    )

    # Sauvegarde par taille
    output_file = output_dir / f"ol_best_combos_{size}_players.csv"
    subset.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✅ Taille {size} joueurs → {len(subset)} combos sauvegardés")

    subset["combo_size"] = size
    all_results.append(subset)

# =========================
# 5. CSV global
# =========================
if all_results:
    global_df = pd.concat(all_results, ignore_index=True)
    global_output = "data/processed/ol_best_combos_ALL_3_to_11.csv"
    global_df.to_csv(global_output, index=False, encoding="utf-8-sig")

    print(f"\n📁 CSV GLOBAL créé : {global_output}")
else:
    print("\n❌ Aucun combo valide trouvé")

print("=== SCRIPT TERMINÉ AVEC SUCCÈS ===")
