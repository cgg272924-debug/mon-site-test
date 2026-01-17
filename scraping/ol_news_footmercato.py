import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.olympique-et-lyonnais.com"
CLUB_URL = BASE_URL


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
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def parse_news(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(" ", strip=True)
        if not title or not href:
            continue
        if "/a" in href or "/article" in href or "/annonce" in href:
            if not href.startswith("http"):
                url = BASE_URL + href
            else:
                url = href
            rows.append(
                {
                    "date": "",
                    "headline": title,
                    "url": url,
                    "source": "O&L",
                }
            )
    return rows


def main() -> None:
    session = get_session()
    html = fetch_html(session, CLUB_URL)
    rows = parse_news(html)
    if not rows:
        print("[footmercato] Aucune actualité parsée", file=sys.stderr)
    df = pd.DataFrame(rows)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_news.csv"
    df.to_csv(out_path, index=False)
    print(out_path)


if __name__ == "__main__":
    main()
