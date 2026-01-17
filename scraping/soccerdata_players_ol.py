from soccerdata import FBref
import pandas as pd
from pathlib import Path

print("=== TELECHARGEMENT STATS JOUEURS OL (FBref via soccerdata) ===")

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

fbref = FBref(
    leagues="FRA-Ligue 1",
    seasons=2025
)

df = fbref.read_player_season_stats(stat_type="standard")

print("=== INFO INDEX ===")
print(df.index.names)

# 🔹 LISTER LES NOMS D'ÉQUIPES DISPONIBLES
teams = df.index.get_level_values("team").unique()
print("\n=== EQUIPES DISPONIBLES ===")
for t in teams:
    print("-", t)

# 🔹 Trouver automatiquement Lyon
team_ol = [t for t in teams if "Lyon" in t][0]
print(f"\n>>> ÉQUIPE OL IDENTIFIÉE : {team_ol}")

# 🔹 Filtrer OL
df_ol = df.xs(team_ol, level="team")

print(f"Joueurs OL trouvés : {len(df_ol)}")

# 🔹 Aplatir colonnes
df_ol.columns = [
    f"{c[0]}_{c[1]}" if c[1] else c[0]
    for c in df_ol.columns
]

# 🔹 Sauvegarde
output_path = RAW_DIR / "ol_players_stats_raw.csv"
df_ol.to_csv(output_path, encoding="utf-8")

print(f"Fichier créé : {output_path}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
