import pandas as pd

print("=== ESTIMATION PROBABILITÉ DE VICTOIRE — OL vs BREST ===")

# =========================
# 1. Charger les données
# =========================
df = pd.read_csv("data/processed/ol_best_combos_ALL_3_to_11.csv")

print(f"Lignes chargées : {len(df)}")
print("Colonnes :", df.columns.tolist())

# =========================
# 2. Filtrer combos fiables
# =========================
df = df[df["matches"] >= 3].copy()

if df.empty:
    raise ValueError("Aucun combo fiable (>=3 matchs)")

# =========================
# 3. Niveau moyen de l'équipe
# =========================
avg_points = df["avg_points"].mean()
avg_score = df["avg_score_final"].mean()

print(f"\n📊 Points moyens estimés : {avg_points:.2f}")
print(f"⚽ Score moyen estimé : {avg_score:.2f}")

# =========================
# 4. Conversion points → probabilités
# =========================
# Hypothèse Ligue 1 :
# 2.3 pts ≈ très fort
# 1.5 pts ≈ moyen
# 0.8 pts ≈ faible

win_prob = min(max(avg_points / 3, 0), 1)

# Répartition réaliste
draw_prob = 0.25 * (1 - abs(avg_points - 1.5) / 1.5)
loss_prob = 1 - win_prob - draw_prob

# Sécurité
win_prob = max(win_prob, 0)
draw_prob = max(draw_prob, 0)
loss_prob = max(loss_prob, 0)

# Normalisation
total = win_prob + draw_prob + loss_prob
win_prob /= total
draw_prob /= total
loss_prob /= total

# =========================
# 5. Résultat final
# =========================
print("\n=== 🔮 ESTIMATION FINALE ===")
print(f"✅ Victoire OL : {win_prob*100:.1f} %")
print(f"➖ Match nul  : {draw_prob*100:.1f} %")
print(f"❌ Défaite OL : {loss_prob*100:.1f} %")

print("\n⚠️ Estimation basée UNIQUEMENT sur les performances internes OL")
print("   (pas de blessures, pas de compo officielle, pas de forme de Brest)")
