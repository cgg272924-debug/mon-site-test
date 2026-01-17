import pandas as pd

print("=== IMPACT ABSENCE JOUEUR CLE ===")

players = pd.read_csv("data/processed/ol_players_rated.csv")
key_players = pd.read_csv("data/processed/ol_key_players.csv")

full_team_rating = players["rating"].mean()

results = []

for _, row in key_players.iterrows():
    player_name = row["player"]

    team_without = players[players["player"] != player_name]
    rating_without = team_without["rating"].mean()

    impact = full_team_rating - rating_without

    results.append({
        "player": player_name,
        "rating_with": round(full_team_rating, 2),
        "rating_without": round(rating_without, 2),
        "impact_points": round(impact, 2)
    })

df_impact = pd.DataFrame(results)

df_impact.to_csv(
    "data/processed/ol_absence_impact.csv",
    index=False
)

print(df_impact)
print("Fichier créé : data/processed/ol_absence_impact.csv")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
