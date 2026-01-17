import sys
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.lequipe.fr"
TEAM_URL = f"{BASE_URL}/Football/Lyon/"
MERCATO_LIVE_URL = f"{BASE_URL}/Football/actu-en-direct/mercato-live/17728"


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) "
                "Gecko/20100101 Firefox/117.0"
            ),
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }
    )
    return session


def fetch_html(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def extract_links_from_team_page(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        if not href:
            continue
        if not href.startswith("http"):
            href_full = BASE_URL + href
        else:
            href_full = href
        label = f"{text} {href_full}".lower()
        if "/football/" not in href_full.lower():
            continue
        if "/video/" in href_full.lower():
            continue
        if "ol " in label or " lyon" in label or "olympique lyonnais" in label:
            if (
                "/football/actualites/" in href_full.lower()
                or "/football/article/" in href_full.lower()
            ):
                links.append(href_full)
    return links


def extract_links_from_mercato_live(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        if not href:
            continue
        if not href.startswith("http"):
            href_full = BASE_URL + href
        else:
            href_full = href
        label = f"{text} {href_full}".lower()
        if "ol " not in label and " lyon" not in label and "olympique lyonnais" not in label:
            continue
        if "/football/" not in href_full.lower():
            continue
        if "/video/" in href_full.lower():
            continue
        if (
            "/football/actualites/" in href_full.lower()
            or "/football/article/" in href_full.lower()
        ):
            links.append(href_full)
    return links


def classify_article(title: str) -> Dict[str, str]:
    t = title.lower()
    category = "rumor"
    direction = "unknown"
    official_keywords = [
        "officiel",
        "officialise",
        "officielle",
        "a signé",
        "a signe",
        "s'engage",
        "s engage",
        "signe à",
        "signe a",
        "prêté",
        "prete",
        "transfert",
    ]
    if any(k in t for k in official_keywords):
        category = "official"
    in_keywords = [
        "à l'ol",
        "a l'ol",
        "a l ol",
        "à lyon",
        "a lyon",
        "rejoindre l'ol",
        "rejoint l'ol",
        "rejoint lyon",
        "s'engage avec l'ol",
        "s engage avec l'ol",
    ]
    out_keywords = [
        "quitte l'ol",
        "quitte lyon",
        "quitte l olympique lyonnais",
        "prêté à",
        "prete a",
        "prêté au",
        "transféré à",
        "transfere a",
    ]
    if any(k in t for k in in_keywords):
        direction = "in"
    elif any(k in t for k in out_keywords):
        direction = "out"
    return {"category": category, "direction": direction}


def parse_article(session: requests.Session, url: str) -> Dict[str, str]:
    html = fetch_html(session, url)
    soup = BeautifulSoup(html, "lxml")
    title = ""
    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
        title = meta_title["content"].strip()
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(" ", strip=True)
    meta_date = soup.find("meta", attrs={"property": "article:published_time"})
    date_str = ""
    if meta_date and meta_date.get("content"):
        date_content = meta_date["content"]
        date_str = date_content.split("T")[0]
    if not date_str:
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            date_str = str(time_tag.get("datetime")).split("T")[0]
        elif time_tag:
            date_str = time_tag.get_text(" ", strip=True)
    cls = classify_article(title)
    if cls["direction"] == "unknown":
        body = soup.get_text(" ", strip=True).lower()
        if "prêté à" in body or "prete a" in body or "transféré à" in body or "transfere a" in body or "signe à" in body or "signe a":
            cls["direction"] = "out"
        elif "s'engage" in body or "s engage" in body or "rejoint l'ol" in body or "rejoint lyon" in body or "arrive à lyon" in body or "arrive a lyon":
            cls["direction"] = "in"
    cls = classify_article(title)
    return {
        "date": date_str,
        "headline": title,
        "category": cls["category"],
        "direction": cls["direction"],
        "url": url,
        "source": "L'Equipe",
    }


def main() -> None:
    session = get_session()
    links = set()
    try:
        html_team = fetch_html(session, TEAM_URL)
        for link in extract_links_from_team_page(html_team):
            links.add(link)
    except Exception as exc:
        print(f"[mercato] Erreur page équipe OL: {exc}", file=sys.stderr)
    try:
        html_live = fetch_html(session, MERCATO_LIVE_URL)
        for link in extract_links_from_mercato_live(html_live):
            links.add(link)
    except Exception as exc:
        print(f"[mercato] Erreur live mercato: {exc}", file=sys.stderr)
    if not links:
        print("[mercato] Aucun article mercato OL détecté", file=sys.stderr)
    rows: List[Dict[str, str]] = []
    for url in sorted(links):
        try:
            rows.append(parse_article(session, url))
            time.sleep(1.5)
        except Exception as exc:
            print(f"[mercato] Erreur article {url}: {exc}", file=sys.stderr)
    if not rows:
        print("[mercato] Aucune donnée à écrire", file=sys.stderr)
        return
    df = pd.DataFrame(rows)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_mercato.csv"
    df = df.sort_values(["date", "headline"], na_position="last")
    df.to_csv(out_path, index=False)
    print(out_path)


if __name__ == "__main__":
    main()
