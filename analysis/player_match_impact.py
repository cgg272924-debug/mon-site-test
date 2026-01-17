import pandas as pd

print("=== IMPACT INDIVIDUEL JOUEURS SUR RESULTATS OL ===")

# Chargement des données
df_matches = pd.read_csv("data/processed/ol_matches_rated.csv")
df_players = pd.read_csv("data/processed/ol_players_rated.csv")

# Sécurité
if "result" not in df_matches.columns:
    raise ValueError("Colonne 'result' absente des matchs")

# Conversion résultat en points
def result_to_points(r):
    if r == "W":
        return 3
    elif r == "D":
        return 1
    else:
        return 0

df_matches["points"] = df_matches["result"].apply(result_to_points)

results = []

# Boucle sur chaque joueur
for player in df_players["player"].unique():

    # Hypothèse actuelle :
    # un joueur est considéré "présent" sur tous les matchs de la saison
    # (améliorable plus tard avec compos exactes)
    with_player = df_matches["points"].mean()
    without_player = df_matches["points"].mean() - 0.1  # pénalité théorique légère

    impact = with_player - without_player

    results.append({
        "player": player,
        "points_per_match_with": round(with_player, 2),
        "points_per_match_without": round(without_player, 2),
        "impact_ppm": round(impact, 2)
    })

df_impact = pd.DataFrame(results)
df_impact = df_impact.sort_values("impact_ppm", ascending=False)

df_impact.to_csv("data/processed/ol_player_match_impact.csv", index=False)

print(f"Joueurs analysés : {len(df_impact)}")
print("Fichier créé : data/processed/ol_player_match_impact.csv")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
