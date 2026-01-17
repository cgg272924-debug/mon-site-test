import sys
from pathlib import Path
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.transfermarkt.us"
OL_INJURIES_URL = f"{BASE_URL}/olympique-lyon/sperrenundverletzungen/verein/1041"


def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }
    )
    return s


def fetch_html(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return r.text


def parse_injuries(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.select("table.items")
    rows: List[Dict[str, str]] = []
    for table in tables:
        tbody = table.find("tbody")
        if not tbody:
            continue
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue
            player_el = tds[0].select_one("a[href*='/profil/spieler/']")
            if not player_el:
                continue
            player = player_el.get_text(strip=True)
            details_parts = [td.get_text(" ", strip=True) for td in tds[1:]]
            details = " | ".join([p for p in details_parts if p])
            rows.append(
                {
                    "team": "Olympique Lyonnais",
                    "player": player,
                    "details": details,
                    "source": OL_INJURIES_URL,
                }
            )
    return rows


def main() -> None:
    print("=== SCRAPING BLESSURES OL (Transfermarkt) ===")
    session = get_session()
    try:
        html = fetch_html(session, OL_INJURIES_URL)
    except Exception as exc:
        print(f"Erreur HTTP: {exc}", file=sys.stderr)
        raise SystemExit(1)
    rows = parse_injuries(html)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_injuries_transfermarkt.csv"
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Fichier créé: {out_path}")


if __name__ == "__main__":
    main()
