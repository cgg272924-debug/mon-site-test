import pandas as pd

print("=== CALCUL NOTE COLLECTIVE OL (JOUEURS) ===")

df_players = pd.read_csv("data/processed/ol_players_rated.csv")

# Note moyenne de l'effectif
team_rating = df_players["rating"].mean()

print(f"Note collective OL (basée sur joueurs) : {team_rating:.2f} / 100")

# Sauvegarde
df_out = pd.DataFrame({
    "team": ["Olympique Lyonnais"],
    "team_rating_players": [round(team_rating, 2)]
})

df_out.to_csv("data/processed/ol_team_rating_players.csv", index=False)

print("Fichier créé : data/processed/ol_team_rating_players.csv")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
