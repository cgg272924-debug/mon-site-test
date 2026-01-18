import asyncio
from datetime import date

import aiohttp
import pandas as pd
from soccerdata import FBref
from understat import Understat

POSITION_EN_TO_FR = {
    "GK": "G",
    "DF": "DC",
    "CB": "DC",
    "LB": "DG",
    "LWB": "DG",
    "RB": "DD",
    "RWB": "DD",
    "WB": "DG",
    "DM": "MDC",
    "CDM": "MDC",
    "MF": "MC",
    "CM": "MC",
    "AM": "MOC",
    "CAM": "MOC",
    "LM": "MG",
    "RM": "MD",
    "LW": "AG",
    "RW": "AD",
    "FW": "BU",
    "ST": "BU",
}


def map_en_to_fr(pos: str) -> str:
    p = str(pos or "").upper()
    primary = p.split(",")[0].strip()
    if not primary:
        return "-"
    return POSITION_EN_TO_FR.get(primary, primary)


def build_fbref_minutes(season_year: int) -> pd.DataFrame:
    print("=== TELECHARGEMENT MINUTES JOUEURS OL (FBref via soccerdata) ===")
    fbref = FBref(leagues="FRA-Ligue 1", seasons=season_year)
    df = fbref.read_player_match_stats(stat_type="summary")
    df = df.reset_index()
    df.columns = [
        "_".join([str(c) for c in col if c != ""]).strip("_")
        if isinstance(col, tuple)
        else col
        for col in df.columns
    ]
    print("Colonnes après flatten :", list(df.columns))
    df_ol = df[df["team"].str.contains("Lyon", case=False, na=False)].copy()
    print(f"✅ Lignes OL trouvées (FBref) : {len(df_ol)}")
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
    df_ol = df_ol.rename(
        columns={
            "min": "minutes_played",
            "Performance_Gls": "goals",
            "Performance_Ast": "assists",
            "Expected_xG": "xg",
            "Expected_xAG": "xag",
        }
    )
    df_ol["pos_fr"] = df_ol["pos"].apply(map_en_to_fr)
    return df_ol


def map_understat_pos_base(pos: str) -> str:
    p = str(pos or "").upper().split()[0]
    if not p:
        return "-"
    if p in ("GK", "G"):
        return "GK"
    if p.startswith("D"):
        return "DF"
    if p.startswith("M"):
        return "MF"
    if p.startswith("F") or p.startswith("S"):
        return "FW"
    return p


async def fetch_understat_players(season_year: int) -> pd.DataFrame:
    async with aiohttp.ClientSession() as session:
        us = Understat(session)
        data = await us.get_league_players(
            "Ligue 1", season_year, {"team_title": "Lyon"}
        )
    df = pd.DataFrame(data or [])
    return df


def build_understat_minutes(season_year: int) -> pd.DataFrame:
    print("=== TELECHARGEMENT MINUTES JOUEURS OL (fallback Understat) ===")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        df_raw = loop.run_until_complete(fetch_understat_players(season_year))
    finally:
        loop.close()
    if df_raw.empty:
        raise RuntimeError("Aucune donnée joueur Understat retournée pour Lyon")
    season_label = f"{season_year}-{season_year + 1}"
    game_label = f"Saison {season_label} (Understat)"
    game_id = f"understat_{season_year}"
    rows = []
    for _, r in df_raw.iterrows():
        player = str(r.get("player_name", "")).strip()
        if not player:
            continue
        team = str(r.get("team_title", "")).strip()
        if not team:
            team = "Lyon"
        pos_raw = str(r.get("position", "")).strip()
        pos_base = map_understat_pos_base(pos_raw)
        try:
            minutes = float(r.get("time", 0) or 0)
        except Exception:
            minutes = 0.0
        try:
            goals = float(r.get("goals", 0) or 0)
        except Exception:
            goals = 0.0
        try:
            assists = float(r.get("assists", 0) or 0)
        except Exception:
            assists = 0.0
        try:
            xg = float(r.get("xG", 0) or 0)
        except Exception:
            xg = 0.0
        try:
            xag = float(r.get("xA", 0) or 0)
        except Exception:
            xag = 0.0
        rows.append(
            {
                "season": season_label,
                "game": game_label,
                "game_id": game_id,
                "team": team,
                "player": player,
                "pos": pos_base,
                "age": "",
                "minutes_played": minutes,
                "goals": goals,
                "assists": assists,
                "xg": xg,
                "xag": xag,
            }
        )
    df_ol = pd.DataFrame(rows)
    print(f"✅ Lignes OL construites (Understat) : {len(df_ol)}")
    df_ol["pos_fr"] = df_ol["pos"].apply(map_en_to_fr)
    return df_ol


print("=== TELECHARGEMENT MINUTES JOUEURS OL (FBref avec fallback Understat) ===")

today = date.today()
season_year = today.year if today.month >= 7 else today.year - 1

try:
    df_ol = build_fbref_minutes(season_year)
except Exception as exc:
    print(f"[AVERTISSEMENT] FBref indisponible, tentative fallback Understat: {exc}")
    df_ol = build_understat_minutes(season_year)

output_path = "data/processed/ol_player_minutes.csv"
df_ol.to_csv(output_path, index=False)

print(f"Fichier créé : {output_path}")
print("=== SCRIPT TERMINE AVEC SUCCES ===")
