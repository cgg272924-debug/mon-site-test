import pandas as pd
from soccerdata import FBref
from datetime import date

print("=== TELECHARGEMENT MINUTES JOUEURS OL (FBref) ===")

today = date.today()
season_year = today.year if today.month >= 7 else today.year - 1
fbref = FBref(leagues="FRA-Ligue 1", seasons=season_year)

# 2. Lecture stats joueurs par match
df = fbref.read_player_match_stats(stat_type="summary")

# 3. Reset index
df = df.reset_index()

# 4. APLATIR LES COLONNES MULTIINDEX ✅
df.columns = [
    "_".join([str(c) for c in col if c != ""]).strip("_")
    if isinstance(col, tuple)
    else col
    for col in df.columns
]

print("Colonnes après flatten :", list(df.columns))

# 5. Filtrer OL
df_ol = df[df["team"].str.contains("Lyon", case=False, na=False)].copy()
print(f"✅ Lignes OL trouvées : {len(df_ol)}")

# 6. Sélection des colonnes utiles
df_ol = df_ol[
    [
        "season",
        "game",
        "game_id",
        "team",
        "player",
        "pos",
        "age",
        "min",
        "Performance_Gls",
        "Performance_Ast",
        "Expected_xG",
        "Expected_xAG",
    ]
]

# 7. Renommage clair
df_ol = df_ol.rename(
    columns={
        "min": "minutes_played",
        "Performance_Gls": "goals",
        "Performance_Ast": "assists",
        "Expected_xG": "xg",
        "Expected_xAG": "xag",
    }
)

# 8. Sauvegarde
output_path = "data/processed/ol_player_minutes.csv"
df_ol.to_csv(output_path, index=False)

print(f"📁 Fichier créé : {output_path}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
