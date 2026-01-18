import pandas as pd
from pathlib import Path
import datetime as dt

print("=== IMPACT ABSENCE JOUEUR CLE ===")

DATA_DIR = Path("data/processed")

players = pd.read_csv(DATA_DIR / "ol_players_rated.csv")
key_players = pd.read_csv(DATA_DIR / "ol_key_players.csv")

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

absence_path = DATA_DIR / "ol_absence_impact.csv"
df_impact.to_csv(absence_path, index=False)

print(df_impact)
print(f"Fichier créé : {absence_path}")

injuries_raw_path = DATA_DIR / "ol_injuries_transfermarkt.csv"
injuries_out_path = DATA_DIR / "ol_injuries.csv"

if injuries_raw_path.exists():
    df_inj_raw = pd.read_csv(injuries_raw_path)
    records = []
    today_str = dt.date.today().isoformat()

    for _, r in df_inj_raw.iterrows():
        player = str(r.get("player", "")).strip()
        details = str(r.get("details", "")).strip()
        if not player or not details:
            continue
        parts = [p.strip() for p in details.split("|")]
        parts = [p for p in parts if p]

        pos = parts[1] if len(parts) >= 2 else ""
        age_raw = parts[2] if len(parts) >= 3 else ""
        injury_type_raw = parts[3] if len(parts) >= 4 else ""
        start_raw = parts[4] if len(parts) >= 5 else ""
        days_raw = parts[5] if len(parts) >= 6 else ""

        try:
            age = int(str(age_raw).split()[0])
        except Exception:
            age = None

        injury_type = injury_type_raw if injury_type_raw and not injury_type_raw.isdigit() else ""

        try:
            start_date = dt.datetime.strptime(start_raw, "%b %d, %Y").date()
            start_date_str = start_date.isoformat()
        except Exception:
            start_date = None
            start_date_str = ""

        try:
            est_days = int(str(days_raw).split()[0])
        except Exception:
            est_days = None

        if start_date and est_days is not None:
            est_return = start_date + dt.timedelta(days=est_days)
            est_return_str = est_return.isoformat()
        else:
            est_return_str = ""

        impact_row = df_impact[df_impact["player"] == player]
        importance = None
        if not impact_row.empty:
            importance = float(impact_row["impact_points"].iloc[0])

        records.append({
            "team": r.get("team", "Olympique Lyonnais"),
            "player": player,
            "position": pos,
            "age": age,
            "injury_type": injury_type,
            "start_date": start_date_str,
            "estimated_return_date": est_return_str,
            "estimated_days": est_days,
            "importance_score": importance,
            "source": r.get("source", ""),
            "last_updated": today_str,
        })

    df_injuries = pd.DataFrame(records)
    df_injuries.to_csv(injuries_out_path, index=False)
    print(f"Fichier créé : {injuries_out_path}")
else:
    print(f"Avertissement: fichier brut blessures introuvable: {injuries_raw_path}")

print("=== SCRIPT TERMINE AVEC SUCCES ===")
