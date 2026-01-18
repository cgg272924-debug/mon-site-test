import os
import random
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment

try:
    from soccerdata import FBref as SD_FBref
except Exception:
    SD_FBref = None


BASE_URL = "https://fbref.com"
COMPETITION_ID = 13
COMPETITION_INDEX_URL = f"{BASE_URL}/en/comps/{COMPETITION_ID}/"

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LIGUE1_STANDINGS_PATH = DATA_DIR / "ligue1_standings.csv"
LIGUE1_MATCHES_PATH = DATA_DIR / "ligue1_matches.csv"
LIGUE1_TEAM_STATS_PATH = DATA_DIR / "ligue1_team_stats.csv"
OL_MATCHES_PATH = DATA_DIR / "ol_matches.csv"
OL_STATS_PATH = DATA_DIR / "ol_stats.csv"


def log(message: str) -> None:
    print(message, flush=True)


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }
    )
    return session


def fetch_url(session: requests.Session, url: str, max_retries: int = 3, timeout: int = 30) -> str:
    last_error: Optional[BaseException] = None
    for attempt in range(1, max_retries + 1):
        try:
            log(f"[HTTP] GET {url} (essai {attempt}/{max_retries})")
            time.sleep(random.uniform(0.8, 2.0))
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.text
            log(f"[HTTP] Statut {response.status_code} pour {url}")
            if response.status_code in (403, 429):
                sleep_s = random.uniform(3.0, 8.0) * attempt
                log(f"[HTTP] Attente {sleep_s:.1f}s (rate-limit)")
                time.sleep(sleep_s)
        except requests.RequestException as exc:
            last_error = exc
            log(f"[HTTP] Erreur réseau pour {url}: {exc}")
        time.sleep(random.uniform(1.5, 4.0) * attempt)
    raise RuntimeError(f"Echec de téléchargement après {max_retries} essais: {url}") from last_error


def iter_fbref_tables(soup: BeautifulSoup) -> Sequence:
    tables: List = []
    for table in soup.find_all("table"):
        tables.append(table)
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment_soup = BeautifulSoup(comment, "lxml")
        for table in comment_soup.find_all("table"):
            tables.append(table)
    return tables


def find_table_with_stats(soup: BeautifulSoup, required_stats: Set[str]) -> BeautifulSoup:
    for table in iter_fbref_tables(soup):
        thead = table.find("thead")
        if not thead:
            continue
        header_cells = thead.find_all(["th", "td"])
        data_stats = {
            cell.get("data-stat")
            for cell in header_cells
            if cell.get("data-stat")
        }
        if required_stats.issubset(data_stats):
            return table
    raise RuntimeError(f"Aucun tableau FBref ne contient les colonnes requises: {sorted(required_stats)}")


def table_to_dataframe(table: BeautifulSoup) -> pd.DataFrame:
    tbody = table.find("tbody")
    if not tbody:
        return pd.DataFrame()
    rows: List[Dict[str, str]] = []
    for row in tbody.find_all("tr"):
        classes = row.get("class") or []
        if "thead" in classes:
            continue
        record: Dict[str, str] = {}
        for cell in row.find_all(["th", "td"]):
            stat = cell.get("data-stat")
            if not stat:
                continue
            value = cell.get_text(" ", strip=True)
            record.setdefault(stat, value)
        if any(value != "" for value in record.values()):
            rows.append(record)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def safe_read_csv(path: Path, date_cols: Optional[Sequence[str]] = None) -> pd.DataFrame:
    try:
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_csv(path)
        if date_cols:
            for c in date_cols:
                if c in df.columns:
                    df[c] = pd.to_datetime(df[c], errors="coerce")
        return df
    except Exception as e:
        log(f"[AVERTISSEMENT] Lecture CSV échouée ({path}): {e}")
        return pd.DataFrame()


def latest_date_from_df(df: pd.DataFrame, col: str) -> Optional[date]:
    if df.empty or col not in df.columns:
        return None
    try:
        s = pd.to_datetime(df[col], errors="coerce").dropna()
        if s.empty:
            return None
        return s.max().date()
    except Exception:
        return None


def detect_new_matches(session: requests.Session, schedule_url: str) -> bool:
    try:
        html = fetch_url(session, schedule_url)
        soup = BeautifulSoup(html, "lxml")
        required_stats = {"date", "home_team", "away_team", "score"}
        table = find_table_with_stats(soup, required_stats)
        df = table_to_dataframe(table)
        if df.empty or "date" not in df.columns:
            return False
        df = df[df["date"] != ""].copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df[df["date"].notna()]
        latest_remote = df["date"].max().date() if not df.empty else None
    except Exception as exc:
        log(f"[INFO] Impossible de détecter nouveaux matchs (FBref): {exc}")
        return False

    existing_paths = [
        LIGUE1_MATCHES_PATH,
        DATA_DIR / "raw" / "ligue1_matches_raw.csv",
    ]
    latest_local: Optional[date] = None
    for p in existing_paths:
        df_local = safe_read_csv(p, date_cols=["date"])
        if not df_local.empty:
            d = latest_date_from_df(df_local, "date")
            if d and (latest_local is None or d > latest_local):
                latest_local = d

    if not latest_remote:
        return False
    if latest_local and latest_remote <= latest_local:
        log(f"[INFO] Pas de nouveaux matchs (local: {latest_local}, remote: {latest_remote})")
        return False
    log(f"[INFO] Nouveaux matchs détectés (local: {latest_local}, remote: {latest_remote})")
    return True


def get_current_season_info(session: requests.Session) -> Dict[str, Optional[str]]:
    html = fetch_url(session, COMPETITION_INDEX_URL)
    soup = BeautifulSoup(html, "lxml")

    table: Optional[BeautifulSoup] = None
    for candidate in iter_fbref_tables(soup):
        if candidate.find("tbody"):
            table = candidate
            break
    if table is None:
        raise RuntimeError("Impossible de trouver le tableau des saisons Ligue 1 sur FBref")

    first_row = table.find("tbody").find("tr")
    if first_row is None:
        raise RuntimeError("Impossible de trouver la ligne de la saison actuelle sur FBref")

    season_cell = first_row.find(["th", "td"])
    season_label = season_cell.get_text(" ", strip=True) if season_cell else "Unknown"

    schedule_url: Optional[str] = None
    standings_url: Optional[str] = None
    team_stats_url: Optional[str] = None

    for a in first_row.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True).lower()
        if ("/schedule" in href or "scores & fixtures" in text or "fixtures" in text) and not schedule_url:
            schedule_url = BASE_URL + href
        elif ("/table" in href or "/standings" in href or "table" in text or "standings" in text) and not standings_url:
            standings_url = BASE_URL + href
        elif ("/stats" in href or "stats" in text) and not team_stats_url:
            team_stats_url = BASE_URL + href

    if not schedule_url:
        raise RuntimeError("Lien calendrier Ligue 1 introuvable sur FBref")

    return {
        "season_label": season_label,
        "schedule_url": schedule_url,
        "standings_url": standings_url,
        "team_stats_url": team_stats_url,
    }


def scrape_ligue1_matches(session: requests.Session, schedule_url: str, season_label: str) -> pd.DataFrame:
    html = fetch_url(session, schedule_url)
    soup = BeautifulSoup(html, "lxml")
    required_stats = {"date", "home_team", "away_team", "score"}
    table = find_table_with_stats(soup, required_stats)
    df = table_to_dataframe(table)
    if df.empty:
        raise RuntimeError("Le tableau des matchs Ligue 1 est vide ou introuvable")

    if "date" not in df.columns:
        raise RuntimeError("Colonne date manquante dans les matchs Ligue 1")

    df = df[df["date"] != ""].copy()
    df["season"] = season_label

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()].copy()
    df["date"] = df["date"].dt.date.astype(str)

    rename_map: Dict[str, str] = {}
    if "week" in df.columns:
        rename_map["week"] = "round"
    if "xg" in df.columns:
        rename_map["xg"] = "home_xg"
    if "xg_opp" in df.columns:
        rename_map["xg_opp"] = "away_xg"
    df = df.rename(columns=rename_map)

    columns_order: List[str] = [
        "season",
        "date",
        "round",
        "home_team",
        "away_team",
        "score",
        "home_xg",
        "away_xg",
        "venue",
        "attendance",
    ]
    available_columns = [c for c in columns_order if c in df.columns]
    for col in df.columns:
        if col not in available_columns:
            available_columns.append(col)
    df_out = df[available_columns].copy()
    return df_out


def scrape_ligue1_standings(session: requests.Session, standings_url: Optional[str], season_label: str) -> pd.DataFrame:
    if not standings_url:
        log("[INFO] Pas de lien de classement détecté, standings ignorés")
        return pd.DataFrame()
    html = fetch_url(session, standings_url)
    soup = BeautifulSoup(html, "lxml")
    required_stats = {"team", "mp", "pts"}
    table = find_table_with_stats(soup, required_stats)
    df = table_to_dataframe(table)
    if df.empty:
        raise RuntimeError("Le tableau de classement Ligue 1 est vide ou introuvable")
    df["season"] = season_label
    return df


def scrape_ligue1_team_stats(session: requests.Session, stats_url: Optional[str], season_label: str) -> pd.DataFrame:
    if not stats_url:
        log("[INFO] Pas de lien de statistiques d'équipes détecté, stats ignorées")
        return pd.DataFrame()
    html = fetch_url(session, stats_url)
    soup = BeautifulSoup(html, "lxml")
    required_stats = {"team"}
    table = find_table_with_stats(soup, required_stats)
    df = table_to_dataframe(table)
    if df.empty:
        raise RuntimeError("Le tableau des statistiques d'équipes est vide ou introuvable")
    df["season"] = season_label
    return df


def build_ol_matches(df_matches: pd.DataFrame) -> pd.DataFrame:
    if df_matches.empty:
        return pd.DataFrame()

    if "home_team" not in df_matches.columns or "away_team" not in df_matches.columns:
        raise RuntimeError("Colonnes home_team ou away_team manquantes dans ligue1_matches")

    mask_home = df_matches["home_team"].str.contains("Lyon", case=False, na=False)
    mask_away = df_matches["away_team"].str.contains("Lyon", case=False, na=False)
    df_ol = df_matches[mask_home | mask_away].copy()

    if df_ol.empty:
        log("[AVERTISSEMENT] Aucun match contenant 'Lyon' trouvé dans ligue1_matches")
        return df_ol

    df_ol["ol_side"] = "home"
    df_ol.loc[mask_away[mask_home | mask_away].index, "ol_side"] = "away"

    def opponent_for_row(row: pd.Series) -> str:
        if row["ol_side"] == "home":
            return str(row.get("away_team", ""))
        return str(row.get("home_team", ""))

    df_ol["opponent"] = df_ol.apply(opponent_for_row, axis=1)

    if "home_xg" in df_ol.columns and "away_xg" in df_ol.columns:
        def ol_xg(row: pd.Series) -> float:
            return float(row["home_xg"]) if row["ol_side"] == "home" else float(row["away_xg"])

        def opp_xg(row: pd.Series) -> float:
            return float(row["away_xg"]) if row["ol_side"] == "home" else float(row["home_xg"])

        df_ol["ol_xg"] = df_ol.apply(ol_xg, axis=1)
        df_ol["opp_xg"] = df_ol.apply(opp_xg, axis=1)

    if "score" in df_ol.columns:
        def compute_result(row: pd.Series) -> str:
            raw_score = str(row["score"])
            parts = re.split(r"[-–]", raw_score)
            if len(parts) != 2:
                return ""
            try:
                home_goals = int(parts[0].strip())
                away_goals = int(parts[1].strip())
            except ValueError:
                return ""
            if row["ol_side"] == "home":
                goals_for = home_goals
                goals_against = away_goals
            else:
                goals_for = away_goals
                goals_against = home_goals
            if goals_for > goals_against:
                return "W"
            if goals_for == goals_against:
                return "D"
            return "L"

        df_ol["result"] = df_ol.apply(compute_result, axis=1)

    return df_ol


def build_ol_stats(df_team_stats: pd.DataFrame) -> pd.DataFrame:
    if df_team_stats.empty:
        return pd.DataFrame()
    if "team" not in df_team_stats.columns:
        raise RuntimeError("Colonne team manquante dans ligue1_team_stats")
    mask = df_team_stats["team"].str.contains("Lyon", case=False, na=False)
    df_ol = df_team_stats[mask].copy()
    if df_ol.empty:
        log("[AVERTISSEMENT] Aucune ligne 'Lyon' trouvée dans ligue1_team_stats")
    return df_ol


def build_key_tuples(df: pd.DataFrame, key_cols: Sequence[str]) -> Set[Tuple]:
    if df.empty:
        return set()
    for col in key_cols:
        if col not in df.columns:
            raise RuntimeError(f"Colonne clé manquante: {col}")
    return set(tuple(df[col] for col in key_cols) for _, df in df[key_cols].iterrows())


def merge_and_write_csv(
    path: Path,
    new_df: pd.DataFrame,
    key_cols: Sequence[str],
    season_col: str,
    season_label: str,
) -> Dict[str, object]:
    if new_df.empty:
        log(f"[INFO] Aucune donnée à écrire pour {path}")
        return {
            "path": str(path),
            "season": season_label,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "total_current_season": 0,
        }

    if season_col not in new_df.columns:
        new_df[season_col] = season_label

    if new_df.duplicated(subset=key_cols).any():
        raise RuntimeError(f"Données dupliquées détectées pour {path.name} sur la saison {season_label}")

    if path.exists():
        existing = pd.read_csv(path)
    else:
        existing = pd.DataFrame(columns=new_df.columns)

    if season_col in existing.columns:
        existing_current = existing[existing[season_col] == season_label].copy()
        existing_other = existing[existing[season_col] != season_label].copy()
    else:
        existing_current = pd.DataFrame(columns=new_df.columns)
        existing_other = existing

    existing_keys = build_key_tuples(existing_current, key_cols)
    new_keys = build_key_tuples(new_df, key_cols)

    added_keys = new_keys - existing_keys
    updated_keys = new_keys & existing_keys
    removed_keys = existing_keys - new_keys

    combined_current = new_df.copy()
    combined = pd.concat([existing_other, combined_current], ignore_index=True)
    combined = combined.drop_duplicates(subset=list(key_cols) + [season_col], keep="last")
    combined.to_csv(path, index=False)

    return {
        "path": str(path),
        "season": season_label,
        "added": len(added_keys),
        "updated": len(updated_keys),
        "removed": len(removed_keys),
        "total_current_season": len(new_keys),
    }


def print_summary(results: List[Dict[str, object]]) -> None:
    log("\n=== RESUME MISE A JOUR DONNEES ===")
    for r in results:
        log(
            f"- {r['path']} (saison {r['season']}): "
            f"{r['total_current_season']} lignes, "
            f"{r['added']} ajoutées, "
            f"{r['updated']} mises à jour, "
            f"{r['removed']} supprimées"
        )


def run_scripts(scripts: Sequence[str]) -> None:
    for script in scripts:
        log(f"[PIPELINE] Execution: {script}")
        result = subprocess.run(["python", script], text=True, capture_output=True)
        if result.stdout:
            log(result.stdout.strip())
        if result.stderr:
            log(result.stderr.strip())
        if result.returncode != 0:
            log(f"[AVERTISSEMENT] Script échoué (continuation): {script}")


def run_git_pipeline() -> None:
    log("\n=== GIT: PREPARATION DU DEPOT ===")

    add_cmd = ["git", "add", "."]
    log(f"[GIT] {' '.join(add_cmd)}")
    add_result = subprocess.run(add_cmd, text=True, capture_output=True)
    if add_result.returncode != 0:
        raise RuntimeError(f"git add a échoué: {add_result.stderr.strip()}")

    commit_cmd = ["git", "commit", "-m", "Update Ligue 1 & OL data (FBref)"]
    log(f"[GIT] {' '.join(commit_cmd)}")
    commit_result = subprocess.run(commit_cmd, text=True, capture_output=True)
    if commit_result.returncode != 0:
        output = (commit_result.stdout or "") + "\n" + (commit_result.stderr or "")
        if "nothing to commit" in output.lower():
            log("[GIT] Aucun changement à valider (nothing to commit)")
        else:
            raise RuntimeError(f"git commit a échoué:\n{output}")

    push_cmd = ["git", "push"]
    log(f"[GIT] {' '.join(push_cmd)}")
    push_result = subprocess.run(push_cmd, text=True, capture_output=True)
    if push_result.returncode != 0:
        raise RuntimeError(f"git push a échoué: {push_result.stderr.strip()}")

    log("[GIT] Depot mis à jour, Netlify peut déclencher le déploiement")


def main() -> None:
    log("=== MISE A JOUR LIGUE 1 & OL (FBref) ===")

    session = get_session()
    is_ci = bool(os.environ.get("GITHUB_ACTIONS"))
    force_scrape = bool(os.environ.get("FORCE_SCRAPE"))
    do_scrape = not is_ci or force_scrape
    season_label = ""
    schedule_url: Optional[str] = None
    standings_url: Optional[str] = None
    team_stats_url: Optional[str] = None
    try:
        season_info = get_current_season_info(session)
        season_label = str(season_info["season_label"])
        schedule_url = str(season_info["schedule_url"])
        standings_url = season_info.get("standings_url")
        team_stats_url = season_info.get("team_stats_url")

        log(f"Saison détectée: {season_label}")
        log(f"URL calendrier: {schedule_url}")
        if standings_url:
            log(f"URL classement: {standings_url}")
        if team_stats_url:
            log(f"URL stats équipes: {team_stats_url}")

        df_matches = pd.DataFrame()
        df_standings = pd.DataFrame()
        df_team_stats = pd.DataFrame()

        if do_scrape:
            if detect_new_matches(session, schedule_url):
                df_matches = scrape_ligue1_matches(session, schedule_url, season_label)
                df_standings = scrape_ligue1_standings(session, standings_url, season_label)
                df_team_stats = scrape_ligue1_team_stats(session, team_stats_url, season_label)
            else:
                log("[INFO] Scraping direct ignoré: aucun nouveau match détecté")
        else:
            log("[INFO] Environnement CI détecté: scraping direct FBref désactivé")
    except Exception as exc:
        log(f"[AVERTISSEMENT] Scraping FBref direct indisponible: {exc}")
        df_matches = pd.DataFrame()
        df_standings = pd.DataFrame()
        df_team_stats = pd.DataFrame()
        today = date.today()
        season_year = today.year if today.month >= 7 else today.year - 1
        season_label = f"{season_year}-{season_year+1}"

    if df_matches.empty or df_standings.empty:
        log("[INFO] Fallback standings via soccerdata")

        def fallback_build_standings() -> pd.DataFrame:
            if SD_FBref is None:
                log("[ERREUR] soccerdata non disponible pour fallback")
                return pd.DataFrame()

            today = date.today()
            season_year = today.year if today.month >= 7 else today.year - 1
            try:
                sd = SD_FBref(leagues="FRA-Ligue 1", seasons=season_year)
                df = sd.read_team_match_stats()
            except Exception as e:
                log(f"[ERREUR] Lecture soccerdata échouée: {e}")
                return pd.DataFrame()

            df = df.reset_index()
            df.columns = [
                "_".join([str(c) for c in col if c != ""]).strip("_")
                if isinstance(col, tuple)
                else str(col)
                for col in df.columns
            ]

            cols = list(df.columns)
            def pick(cands: List[str]) -> Optional[str]:
                for c in cands:
                    for col in cols:
                        if col.lower() == c.lower():
                            return col
                return None

            k_team = pick(["team", "squad"])
            k_result = pick(["result"])
            k_gf = pick(["GF", "goals_for"])
            k_ga = pick(["GA", "goals_against"])

            if not k_team or not k_result:
                log("[ERREUR] Colonnes indispensables absentes dans soccerdata")
                return pd.DataFrame()

            df = df[df[k_result].notna() & (df[k_result] != "")].copy()
            df[k_gf] = pd.to_numeric(df.get(k_gf, 0), errors="coerce").fillna(0)
            df[k_ga] = pd.to_numeric(df.get(k_ga, 0), errors="coerce").fillna(0)

            agg = df.groupby(k_team).agg(
                matches=(k_result, "count"),
                wins=(k_result, lambda s: (s == "W").sum()),
                draws=(k_result, lambda s: (s == "D").sum()),
                losses=(k_result, lambda s: (s == "L").sum()),
                goals_for=(k_gf, "sum"),
                goals_against=(k_ga, "sum"),
            ).reset_index().rename(columns={k_team: "team"})
            agg["goal_difference"] = agg["goals_for"] - agg["goals_against"]
            agg["points"] = agg["wins"] * 3 + agg["draws"]
            agg["points_per_match"] = (agg["points"] / agg["matches"]).round(2)
            agg["win_rate"] = ((agg["wins"] / agg["matches"]) * 100).round(1)
            agg["goals_for_per_match"] = (agg["goals_for"] / agg["matches"]).round(2)
            agg["goals_against_per_match"] = (agg["goals_against"] / agg["matches"]).round(2)

            agg = agg.sort_values(
                ["points", "goal_difference", "goals_for"],
                ascending=False
            ).reset_index(drop=True)
            agg["rank"] = agg.index + 1

            agg.to_csv(LIGUE1_STANDINGS_PATH, index=False)
            log(f"[INFO] Ecrit fallback standings: {LIGUE1_STANDINGS_PATH}")
            return agg

        df_standings = fallback_build_standings()

    df_ol_matches = build_ol_matches(df_matches)
    df_ol_stats = build_ol_stats(df_team_stats)

    results: List[Dict[str, object]] = []

    results.append(
        merge_and_write_csv(
            LIGUE1_MATCHES_PATH,
            df_matches,
            key_cols=["season", "date", "home_team", "away_team"],
            season_col="season",
            season_label=season_label,
        )
    )

    if not df_standings.empty:
        results.append(
            merge_and_write_csv(
                LIGUE1_STANDINGS_PATH,
                df_standings,
                key_cols=["season", "team"],
                season_col="season",
                season_label=season_label,
            )
        )

    if not df_team_stats.empty:
        results.append(
            merge_and_write_csv(
                LIGUE1_TEAM_STATS_PATH,
                df_team_stats,
                key_cols=["season", "team"],
                season_col="season",
                season_label=season_label,
            )
        )

    if not df_ol_matches.empty:
        results.append(
            merge_and_write_csv(
                OL_MATCHES_PATH,
                df_ol_matches,
                key_cols=["season", "date", "ol_side", "opponent"],
                season_col="season",
                season_label=season_label,
            )
        )

    if not df_ol_stats.empty:
        results.append(
            merge_and_write_csv(
                OL_STATS_PATH,
                df_ol_stats,
                key_cols=["season", "team"],
                season_col="season",
                season_label=season_label,
            )
        )

    print_summary(results)

    try:
        scripts_analysis = [
            "analysis/clean_matches.py",
            "analysis/match_rating.py",
            "analysis/match_score_final.py",
            "analysis/step0_create_match_key.py",
            "analysis/step1_build_lineups.py",
            "analysis/step2_create_combos_per_match.py",
            "analysis/step3_analyze_combos.py",
            "analysis/analyze_best_combos.py",
            "analysis/lineup_impact_step1_FIX.py",
            "analysis/lineup_impact_step2.py",
            "analysis/stepA_create_league1_standings.py",
            "scraping/get_league1_standings_home_away.py",
            "scraping/ol_injuries_transfermarkt.py",
            "analysis/absence_impact.py",
        ]
        scripts_scraping_soccerdata = [
            "scraping/soccerdata_ligue1.py",
            "scraping/soccerdata_player_minutes_ol.py",
        ]
        new_matches_for_soccerdata = False
        if do_scrape and schedule_url:
            if detect_new_matches(session, schedule_url):
                new_matches_for_soccerdata = True
            else:
                log("[INFO] Scraping soccerdata ignoré: aucun nouveau match détecté")
        elif do_scrape and not schedule_url:
            log("[INFO] Scraping soccerdata ignoré: URL calendrier indisponible")
        if do_scrape and new_matches_for_soccerdata:
            run_scripts(scripts_scraping_soccerdata)
        run_scripts(scripts_analysis)
    except Exception as exc:
        log(f"[AVERTISSEMENT] Etape analyse interrompue: {exc}")
        # Pas d'arrêt: le pipeline ne doit pas crasher
        pass

    try:
        run_git_pipeline()
    except Exception as exc:
        log(f"[AVERTISSEMENT] Etape Git interrompue: {exc}")
        sys.exit(1)

    log("=== MISE A JOUR TERMINEE AVEC SUCCES ===")


if __name__ == "__main__":
    main()
