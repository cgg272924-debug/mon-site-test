import pandas as pd
from pathlib import Path
import re

print("=== RECUPERATION CLASSEMENT LIGUE 1 (DOMICILE/EXTERIEUR) ===")

# Création des dossiers si nécessaire
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

raw_output = RAW_DIR / "ligue1_matches_raw.csv"

# Chargement des données existantes
if not raw_output.exists():
    print(f"ERREUR: Le fichier {raw_output} n'existe pas.")
    print("Veuillez d'abord executer soccerdata_ligue1.py pour telecharger les donnees.")
    exit(1)

print(f"Chargement des donnees depuis {raw_output}...")
df_matches = pd.read_csv(raw_output)
print(f"OK - {len(df_matches)} lignes chargees")

# Fonction pour extraire le nom de l'équipe depuis match_report
def get_team_from_match(row):
    """Extrait le nom de l'équipe depuis match_report et venue"""
    match_report = str(row.get("match_report", ""))
    venue = row.get("venue", "")
    opponent = str(row.get("opponent", ""))
    
    if not match_report or match_report == "nan":
        return None
    
    try:
        # Format: /en/matches/xxx/Equipe1-Equipe2-Mois-Jour-Annee-Ligue-1
        # Exemple: /en/matches/c69996e3/Angers-Paris-FC-August-17-2025-Ligue-1
        url_part = match_report.split("/")[-1]
        
        # Enlever le suffixe "-Ligue-1"
        url_part = url_part.replace("-Ligue-1", "")
        
        # Enlever la date (format: -Mois-Jour-Annee)
        # Pattern: -MonthName-DayNumber-YearNumber
        url_part = re.sub(r'-[A-Z][a-z]+-\d+-\d+$', '', url_part)
        
        # Maintenant on a: Equipe1-Equipe2 (avec tirets)
        # Il faut séparer les deux équipes en utilisant l'opponent
        parts = url_part.split("-")
        opponent_parts = opponent.replace(" ", "-").split("-")
        
        # Trouver où se trouve l'opponent dans les parts
        # L'opponent peut être composé de plusieurs mots avec tirets
        opponent_start_idx = None
        for i in range(len(parts) - len(opponent_parts) + 1):
            if parts[i:i+len(opponent_parts)] == opponent_parts:
                opponent_start_idx = i
                break
        
        if opponent_start_idx is not None:
            # On a trouvé l'opponent, l'équipe est l'autre partie
            if venue == "Home":
                # L'équipe home est avant l'opponent
                team_parts = parts[:opponent_start_idx]
            else:
                # L'équipe away est après l'opponent
                team_parts = parts[opponent_start_idx + len(opponent_parts):]
            
            if team_parts:
                team = " ".join(team_parts)
                return team.strip()
        
        # Si on n'a pas trouvé avec l'opponent, utiliser une heuristique simple
        # Pour la plupart des cas, si venue=Home, l'équipe est au début
        # Si venue=Away, l'équipe est à la fin
        if len(parts) >= 2:
            # Essayer de trouver une séparation logique
            # Généralement, la première équipe est 1-2 mots, la deuxième aussi
            # On va chercher où pourrait être la séparation
            
            # Méthode simple: si on connaît l'opponent, chercher ses mots
            opponent_lower = opponent.lower()
            for i in range(1, len(parts)):
                # Tester si les parties après i correspondent à l'opponent
                potential_opponent = " ".join(parts[i:]).lower()
                if opponent_lower in potential_opponent or potential_opponent in opponent_lower:
                    if venue == "Home":
                        return " ".join(parts[:i]).strip()
                    else:
                        return " ".join(parts[i:]).strip()
            
            # Si toujours pas trouvé, utiliser une séparation au milieu
            mid = len(parts) // 2
            if venue == "Home":
                return " ".join(parts[:mid]).strip()
            else:
                return " ".join(parts[mid:]).strip()
                
    except Exception as e:
        print(f"Erreur extraction equipe pour {match_report}: {e}")
        return None
    
    return None

# Fonction pour calculer les points
def get_points(result):
    if result == "W":
        return 3
    elif result == "D":
        return 1
    return 0

# Traitement des données pour créer le classement
print("\nCalcul du classement...")

# Préparation des données
standings_data = []

for idx, row in df_matches.iterrows():
    team = get_team_from_match(row)
    venue = row.get("venue", "")
    result = row.get("result", "")
    gf = pd.to_numeric(row.get("GF", 0), errors="coerce") or 0
    ga = pd.to_numeric(row.get("GA", 0), errors="coerce") or 0
    
    if not team or pd.isna(venue) or pd.isna(result):
        if idx < 5:  # Afficher les erreurs pour les premières lignes seulement
            print(f"Ligne {idx}: team={team}, venue={venue}, result={result}")
        continue
    
    points = get_points(result)
    
    # Stats générales
    standings_data.append({
        "team": team,
        "venue": "All",
        "matches": 1,
        "wins": 1 if result == "W" else 0,
        "draws": 1 if result == "D" else 0,
        "losses": 1 if result == "L" else 0,
        "goals_for": gf,
        "goals_against": ga,
        "points": points
    })
    
    # Stats domicile
    if venue == "Home":
        standings_data.append({
            "team": team,
            "venue": "Home",
            "matches": 1,
            "wins": 1 if result == "W" else 0,
            "draws": 1 if result == "D" else 0,
            "losses": 1 if result == "L" else 0,
            "goals_for": gf,
            "goals_against": ga,
            "points": points
        })
    
    # Stats extérieur
    elif venue == "Away":
        standings_data.append({
            "team": team,
            "venue": "Away",
            "matches": 1,
            "wins": 1 if result == "W" else 0,
            "draws": 1 if result == "D" else 0,
            "losses": 1 if result == "L" else 0,
            "goals_for": gf,
            "goals_against": ga,
            "points": points
        })

# Création du DataFrame
df_standings = pd.DataFrame(standings_data)

if len(df_standings) == 0:
    print("ERREUR: Aucune donnee valide trouvee. Verifiez l'extraction des noms d'equipes.")
    exit(1)

# Agrégation par équipe et type de match
standings_agg = (
    df_standings.groupby(["team", "venue"], as_index=False)
    .agg({
        "matches": "sum",
        "wins": "sum",
        "draws": "sum",
        "losses": "sum",
        "goals_for": "sum",
        "goals_against": "sum",
        "points": "sum"
    })
)

# Calcul des statistiques supplémentaires
standings_agg["goal_difference"] = standings_agg["goals_for"] - standings_agg["goals_against"]
standings_agg["points_per_match"] = (standings_agg["points"] / standings_agg["matches"]).round(2)
standings_agg["win_rate"] = (standings_agg["wins"] / standings_agg["matches"] * 100).round(1)
standings_agg["goals_for_per_match"] = (standings_agg["goals_for"] / standings_agg["matches"]).round(2)
standings_agg["goals_against_per_match"] = (standings_agg["goals_against"] / standings_agg["matches"]).round(2)

# Réorganisation des colonnes
standings_agg = standings_agg[[
    "team",
    "venue",
    "matches",
    "wins",
    "draws",
    "losses",
    "goals_for",
    "goals_against",
    "goal_difference",
    "points",
    "points_per_match",
    "win_rate",
    "goals_for_per_match",
    "goals_against_per_match"
]]

# Tri : d'abord par type (All, Home, Away), puis par points décroissants
standings_agg = standings_agg.sort_values(
    ["venue", "points", "goal_difference", "goals_for"],
    ascending=[True, False, False, False]
).reset_index(drop=True)

# Ajout du rang pour chaque type de match
standings_agg["rank"] = standings_agg.groupby("venue").cumcount() + 1

# Sauvegarde du format long (All + Home + Away)
output_path_long = Path("data/processed/league1_standings_home_away_long.csv")
output_path_long.parent.mkdir(parents=True, exist_ok=True)
standings_agg.to_csv(output_path_long, index=False, encoding="utf-8")
print(f"\nOK - Format long sauvegarde : {output_path_long}")

# Création d'un format large : une ligne par équipe avec colonnes séparées pour Home/Away
print("\nCreation du format large (une ligne par equipe)...")

# Séparation des données par type
df_all = standings_agg[standings_agg["venue"] == "All"].copy()
df_home = standings_agg[standings_agg["venue"] == "Home"].copy()
df_away = standings_agg[standings_agg["venue"] == "Away"].copy()

# Renommage des colonnes pour Home
home_cols = {col: f"home_{col}" for col in df_home.columns if col != "team"}
df_home = df_home.rename(columns=home_cols)

# Renommage des colonnes pour Away
away_cols = {col: f"away_{col}" for col in df_away.columns if col != "team"}
df_away = df_away.rename(columns=away_cols)

# Fusion des données
df_wide = df_all.merge(df_home[["team"] + [f"home_{col}" for col in home_cols.keys()]], on="team", how="left")
df_wide = df_wide.merge(df_away[["team"] + [f"away_{col}" for col in away_cols.keys()]], on="team", how="left")

# Réorganisation des colonnes : général, puis home, puis away
cols_order = ["rank", "team", "matches", "wins", "draws", "losses", "goals_for", "goals_against", 
              "goal_difference", "points", "points_per_match", "win_rate", 
              "goals_for_per_match", "goals_against_per_match"]

home_cols_order = [f"home_{col}" for col in cols_order if col != "team"]
away_cols_order = [f"away_{col}" for col in cols_order if col != "team"]

final_cols = cols_order + home_cols_order + away_cols_order
df_wide = df_wide[[col for col in final_cols if col in df_wide.columns]]

# Tri par classement général
df_wide = df_wide.sort_values("rank").reset_index(drop=True)

# Sauvegarde du format large
output_path_wide = Path("data/processed/league1_standings_home_away.csv")
df_wide.to_csv(output_path_wide, index=False, encoding="utf-8")

print(f"OK - Format large sauvegarde : {output_path_wide}")
print(f"Nombre total d'equipes : {len(df_wide)}")

# Affichage du top 5 général
print("\nTOP 5 CLASSEMENT GENERAL :")
for _, row in df_wide.head(5).iterrows():
    goal_diff = int(row['goal_difference']) if not pd.isna(row['goal_difference']) else 0
    print(f"{int(row['rank'])}. {row['team']} - {int(row['points'])} pts ({int(row['matches'])} matchs, "
          f"{int(row['wins'])}V-{int(row['draws'])}N-{int(row['losses'])}D, "
          f"Diff: {goal_diff:+d})")
    home_pts = int(row.get('home_points', 0)) if not pd.isna(row.get('home_points', 0)) else 0
    home_m = int(row.get('home_matches', 0)) if not pd.isna(row.get('home_matches', 0)) else 0
    away_pts = int(row.get('away_points', 0)) if not pd.isna(row.get('away_points', 0)) else 0
    away_m = int(row.get('away_matches', 0)) if not pd.isna(row.get('away_matches', 0)) else 0
    print(f"   Domicile: {home_pts} pts ({home_m} matchs) | "
          f"Exterieur: {away_pts} pts ({away_m} matchs)")

print("\n=== SCRIPT TERMINE AVEC SUCCES ===")
