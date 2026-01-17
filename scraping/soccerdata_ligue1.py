from soccerdata import FBref
import pandas as pd

print("=== TELECHARGEMENT MATCHS LIGUE 1 (FBref via soccerdata) ===")

fbref = FBref(
    leagues="FRA-Ligue 1",
    seasons=2025
)

df_matches = fbref.read_team_match_stats()

output_path = "data/raw/ligue1_matches_raw.csv"
df_matches.to_csv(output_path, index=False)

print("✅ Fichier créé avec succès")
print(f"📁 Chemin : {output_path}")
print(f"📊 Nombre de lignes : {len(df_matches)}")
