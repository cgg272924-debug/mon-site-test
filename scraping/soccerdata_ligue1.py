from soccerdata import FBref
import pandas as pd
from datetime import date

print("=== TELECHARGEMENT MATCHS LIGUE 1 (FBref via soccerdata) ===")

today = date.today()
season_year = today.year if today.month >= 7 else today.year - 1
fbref = FBref(leagues="FRA-Ligue 1", seasons=season_year)

df_matches = fbref.read_team_match_stats()

output_path = "data/raw/ligue1_matches_raw.csv"
df_matches.to_csv(output_path, index=False)

print("Fichier créé avec succès")
print(f"Chemin : {output_path}")
print(f"Nombre de lignes : {len(df_matches)}")
