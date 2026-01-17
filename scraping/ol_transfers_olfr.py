import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.ol.fr"
NEWS_URL = f"{BASE_URL}/actualites"


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


def classify(headline: str, body: str = "") -> Dict[str, str]:
    t = (headline or "").lower()
    b = (body or "").lower()
    direction = "unknown"
    in_keys = ["signe", "s'engage", "s engage", "rejoint", "arrive", "vient", "signature"]
    out_keys = ["quitte", "prêté à", "prete a", "prêté au", "transféré à", "transfere a", "poursuit ailleurs"]
    if any(k in t for k in in_keys) or any(k in b for k in in_keys):
        direction = "in"
    if any(k in t for k in out_keys) or any(k in b for k in out_keys):
        direction = "out"
    return {"direction": direction}

def parse_official_list(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(" ", strip=True)
        if not href or not txt:
            continue
        label = f"{txt} {href}".lower()
        if "actualites" in href or "/news" in href or "/article" in href:
            if any(k in label for k in ["mercato", "transfert", "signe", "rejoint", "quitte", "prêt"]):
                url = href if href.startswith("http") else BASE_URL + href
                if url not in links:
                    links.append(url)
    rows: List[Dict[str, str]] = []
    return links


def main() -> None:
    s = get_session()
    html = fetch_html(s, NEWS_URL)
    links = parse_official_list(html)
    if not links:
        print("[ol.fr] Aucun lien de transfert détecté", file=sys.stderr)
    rows: List[Dict[str, str]] = []
    for url in links:
        try:
            page = fetch_html(s, url)
            soup = BeautifulSoup(page, "lxml")
            title = ""
            meta_title = soup.find("meta", property="og:title")
            if meta_title and meta_title.get("content"):
                title = meta_title["content"].strip()
            if not title:
                tag_title = soup.find("title")
                if tag_title:
                    title = tag_title.get_text(" ", strip=True)
            body_text = soup.get_text(" ", strip=True)
            cls = classify(title, body_text)
            date_str = ""
            meta_date = soup.find("meta", attrs={"property": "article:published_time"})
            if meta_date and meta_date.get("content"):
                date_str = str(meta_date["content"]).split("T")[0]
            if not date_str:
                time_tag = soup.find("time")
                if time_tag and time_tag.get("datetime"):
                    date_str = str(time_tag.get("datetime")).split("T")[0]
            rows.append(
                {
                    "date": date_str,
                    "headline": title,
                    "direction": cls["direction"],
                    "fee": "",
                    "url": url,
                    "source": "OL.fr",
                }
            )
        except Exception as exc:
            print(f"[ol.fr] Erreur parse {url}: {exc}", file=sys.stderr)
    df = pd.DataFrame(rows)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_transfers_official.csv"
    df.to_csv(out_path, index=False)
    print(out_path)


if __name__ == "__main__":
    main()
