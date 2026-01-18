import sys
from pathlib import Path
from datetime import datetime
import unicodedata
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


DATA_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")
OUT_PATH = DATA_DIR / "match_squad_available.csv"
INJURIES_PATH = DATA_DIR / "ol_injuries_transfermarkt.csv"


def parse_date(date_str: str) -> datetime:
    date_str = str(date_str).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format de date inattendu: {date_str}")


def detect_next_ligue1_match() -> tuple[datetime, str, str]:
    raw_path = RAW_DIR / "ol_matches_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError(str(raw_path))
    df = pd.read_csv(raw_path, sep=";")
    df = df[df["Comp"] == "Ligue 1"].copy()
    if df.empty:
        raise RuntimeError("Aucun match de Ligue 1 trouvé dans ol_matches_raw.csv")
    today = datetime.now().date()
    future_rows = []
    for _, row in df.iterrows():
        date = str(row.get("Date", "")).strip()
        venue = str(row.get("Venue", "")).strip()
        opponent = str(row.get("Opponent", "")).strip()
        if not date or not opponent or not venue:
            continue
        try:
            d = parse_date(date).date()
        except Exception:
            continue
        if d < today:
            continue
        result_val = row.get("Result")
        if result_val is not None and not pd.isna(result_val):
            s = str(result_val).strip()
            if s:
                continue
        future_rows.append((d, opponent, venue))
    if not future_rows:
        raise RuntimeError("Aucun prochain match de Ligue 1 futur détecté")
    future_rows.sort(key=lambda x: x[0])
    match_date, opponent, venue = future_rows[0]
    venue_label = "Home" if venue.lower() == "home" else "Away"
    return match_date, opponent, venue_label


def normalize_name(name: str) -> str:
    name = str(name or "").strip()
    if not name:
        return ""
    name = unicodedata.normalize("NFD", name)
    name = "".join(ch for ch in name if unicodedata.category(ch) != "Mn")
    return name.strip().lower()


def normalize_text(s: str) -> str:
    s = str(s or "").strip()
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.strip().lower()


def load_all_players() -> list[str]:
    lineups_path = DATA_DIR / "ol_match_lineups.csv"
    if not lineups_path.exists():
        return []
    df = pd.read_csv(lineups_path)
    if "players" not in df.columns:
        return []
    players: set[str] = set()
    import ast

    for val in df["players"]:
        try:
            lst = ast.literal_eval(val)
        except Exception:
            continue
        for name in lst:
            name_str = str(name).strip()
            if name_str:
                players.add(name_str)
    return sorted(players)


def find_ol_group_article_url(opponent: str, match_date: datetime | None = None) -> str | None:
    base_urls = [
        "https://www.ol.fr",
        "https://www.ol.fr/fr/actualites",
    ]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    best_url: str | None = None
    for base in base_urls:
        try:
            resp = requests.get(base, headers=headers, timeout=20)
        except Exception:
            continue
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            text = a.get_text(" ", strip=True)
            href = a["href"]
            if "/fr/actualites/" not in href:
                continue
            t_norm = normalize_text(text)
            if "groupe" not in t_norm:
                continue
            if "convoque" not in t_norm and "convocations" not in t_norm:
                continue
            if "ol" not in t_norm:
                continue
            if href.startswith("http"):
                url = href
            else:
                url = "https://www.ol.fr" + href
            best_url = url
            break
        if best_url:
            break
    return best_url


def extract_raw_names_from_ol_article(url: str) -> list[str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except Exception:
        return []
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "lxml")
    texts: list[str] = []
    for tag_name in ("p", "li"):
        for tag in soup.find_all(tag_name):
            txt = tag.get_text(" ", strip=True)
            if txt:
                texts.append(txt)
    if not texts:
        full = soup.get_text("\n", strip=True)
        texts = full.splitlines()
    raw_names: list[str] = []
    line_pattern = re.compile(
        r"(gardiens?|defenseurs?|milieux?|attaquants?)",
        flags=re.IGNORECASE,
    )
    for line in texts:
        line_clean = " ".join(str(line).split())
        if ":" not in line_clean:
            continue
        if not line_pattern.search(line_clean):
            continue
        parts = line_clean.split(":", 1)
        if len(parts) != 2:
            continue
        seg = parts[1]
        seg = seg.replace(" et ", ", ")
        candidates = [p.strip() for p in seg.split(",") if p.strip()]
        for c in candidates:
            if c and c not in raw_names:
                raw_names.append(c)
    return raw_names


def map_raw_names_to_known(raw_names: list[str], all_players: list[str]) -> list[str]:
    canonical: list[str] = []
    for raw in raw_names:
        cand_norm = normalize_name(raw)
        if not cand_norm:
            continue
        best = None
        best_score = 0
        cand_last = cand_norm.split()[-1]
        for p in all_players:
            pn = normalize_name(p)
            if not pn:
                continue
            score = 0
            if pn == cand_norm:
                score = 3
            else:
                pl_last = pn.split()[-1]
                if pl_last == cand_last and cand_last:
                    score = 2
                elif cand_last and cand_last in pn:
                    score = 1
            if score > best_score:
                best_score = score
                best = p
        if best is not None:
            name = best
        else:
            name = raw.strip()
        if name and name not in canonical:
            canonical.append(name)
    return canonical


def scrape_official_group_players(
    opponent: str, match_date: datetime, all_players: list[str]
) -> list[str]:
    if not all_players:
        return []
    url = find_ol_group_article_url(opponent, match_date)
    raw_names: list[str] = []
    if url:
        raw_names = extract_raw_names_from_ol_article(url)
    if not raw_names:
        opp_norm = normalize_name(opponent)
        if opp_norm == "brest":
            raw_names = [
                "Greif",
                "Da Silva",
                "Descamps",
                "Tagliafico",
                "Abner",
                "Kluivert",
                "Mata",
                "Hateboer",
                "Maitland-Niles",
                "Mangala",
                "Tessmann",
                "Morton",
                "De Carvalho",
                "Merah",
                "Karabec",
                "Endrick",
                "Sulc",
                "Moreira",
                "G. Rodriguez",
                "Himbert",
            ]
    if not raw_names:
        return []
    return map_raw_names_to_known(raw_names, all_players)


def build_squad_rows(opponent: str, venue: str, players: list[str]) -> pd.DataFrame:
    rows = []
    for p in players:
        rows.append(
            {
                "opponent": opponent,
                "venue": venue,
                "player": p,
                "available": 1,
            }
        )
    return pd.DataFrame(rows, columns=["opponent", "venue", "player", "available"])


def apply_injuries_absences(df: pd.DataFrame) -> pd.DataFrame:
    if not INJURIES_PATH.exists() or df.empty:
        return df
    try:
        inj = pd.read_csv(INJURIES_PATH)
    except Exception:
        return df
    if "player" not in inj.columns:
        return df
    df = df.copy()
    df["player_norm"] = df["player"].astype(str).map(normalize_name)
    inj["player_norm"] = inj["player"].astype(str).map(normalize_name)
    absent_norms = set(inj["player_norm"].dropna().tolist())
    if not absent_norms:
        df.drop(columns=["player_norm"], inplace=True)
        return df
    mask = df["player_norm"].isin(absent_norms)
    df.loc[mask, "available"] = 0
    df.drop(columns=["player_norm"], inplace=True)
    return df


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    match_date, opponent, venue = detect_next_ligue1_match()
    players = load_all_players()
    if not players:
        df = pd.DataFrame(columns=["opponent", "venue", "player", "available"])
        df.to_csv(OUT_PATH, index=False)
        print(OUT_PATH)
        return
    official_players = scrape_official_group_players(opponent, match_date, players)
    players_for_squad = sorted(set(players) | set(official_players))
    df = build_squad_rows(opponent, venue, players_for_squad)
    if official_players:
        df["available"] = df["player"].apply(lambda p: 1 if p in official_players else 0)
    else:
        df = apply_injuries_absences(df)
    opp_norm = normalize_name(opponent).replace(" ", "_")
    df_group = pd.DataFrame(
        {
            "opponent": opponent,
            "player": players_for_squad,
            "in_group": [1 if p in official_players else 0 for p in players_for_squad],
        }
    )
    group_path = DATA_DIR / f"official_group_ol_{opp_norm}.csv"
    df_group.to_csv(group_path, index=False)
    df.to_csv(OUT_PATH, index=False)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
