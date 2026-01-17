import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.transfermarkt.com"
TEAM_PATH = "/olympique-lyon/transfers/verein/1041"


def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9,fr-FR;q=0.8",
        }
    )
    return s


def fetch_html(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def _to_iso(date_text: str) -> str:
    if not date_text:
        return ""
    for fmt in ("%b %d, %Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_text.strip(), fmt).date().isoformat()
        except Exception:
            continue
    return ""


def _abs_url(href: str) -> str:
    if not href:
        return ""
    return href if href.startswith("http") else f"{BASE_URL}{href}"


def _fetch_transfer_date(session: requests.Session, url: str) -> str:
    if not url:
        return ""
    try:
        html = fetch_html(session, _abs_url(url))
        soup = BeautifulSoup(html, "lxml")
        tbody = soup.select_one("table.items tbody") or soup.select_one("table.responsive-table tbody")
        if not tbody:
            return ""
        trs = tbody.find_all("tr")
        if not trs:
            return ""
        tds = trs[0].find_all("td")
        if not tds:
            return ""
        date_candidate = tds[0].get_text(" ", strip=True)
        iso = _to_iso(date_candidate)
        if iso:
            return iso
        parts = [p for p in date_candidate.split() if any(ch.isdigit() for ch in p)]
        if parts:
            iso = _to_iso(" ".join(parts))
            if iso:
                return iso
        return ""
    except Exception:
        return ""


def parse_transfers(session: requests.Session, html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict[str, str]] = []
    boxes = soup.find_all("div", class_="box")
    for box in boxes:
        h2 = box.find("h2")
        if not h2:
            continue
        title = h2.get_text(" ", strip=True).lower()
        if (
            "arriv" in title
            or "entr" in title
            or "ins" in title
            or "arrival" in title
            or "arrivals" in title
        ):
            direction = "in"
        elif (
            "départ" in title
            or "sortie" in title
            or "outs" in title
            or "departure" in title
            or "departures" in title
        ):
            direction = "out"
        else:
            continue
        table = box.find("table", class_="items") or box.find(
            "table", class_="responsive-table"
        )
        if not table:
            continue
        tbody = table.find("tbody")
        if not tbody:
            continue
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if not tds:
                continue
            player = ""
            if len(tds) >= 2:
                player_cell = tds[1]
                a_player = player_cell.select_one('a[href*="/profil/spieler/"]') or player_cell.select_one("td.hauptlink a[href*='/profil/spieler/']")
                if a_player:
                    player = a_player.get_text(" ", strip=True).strip()
            if not player:
                continue
            fee = ""
            td_fee = tr.select_one("td.rechts, td.right, td.transfersum") or (tds[-1] if tds else None)
            if td_fee:
                fee = td_fee.get_text(" ", strip=True)
            if player and fee and player.lower() == fee.lower():
                fee = ""
            link_fee: Optional[str] = None
            a_fee = td_fee.select_one("a[href]") if td_fee else None
            if a_fee and a_fee.get("href"):
                link_fee = a_fee["href"]
            date = ""
            rows.append(
                {
                    "date": date,
                    "headline": player,
                    "direction": direction,
                    "fee": fee,
                    "url": link_fee or "",
                    "source": "Transfermarkt",
                }
            )
    return rows


def filter_current_season(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    year = datetime.now().year
    season_year = year if datetime.now().month >= 7 else year - 1
    out: List[Dict[str, str]] = []
    for r in rows:
        out.append(r)
    return out


def main() -> None:
    session = get_session()
    year = datetime.now().year
    season_year = year if datetime.now().month >= 7 else year - 1
    season_url = f"{BASE_URL}{TEAM_PATH}/plus/0?saison_id={season_year}"
    html = fetch_html(session, season_url)
    try:
        root = Path(__file__).resolve().parent.parent
        dbg_path = root / "data" / "processed" / "_debug_transfermarkt.html"
        dbg_path.parent.mkdir(parents=True, exist_ok=True)
        dbg_path.write_text(html, encoding="utf-8")
    except Exception:
        pass
    rows = parse_transfers(session, html)
    rows = filter_current_season(rows)
    unique: Dict[str, Dict[str, str]] = {}
    for r in rows:
        key = f"{r.get('headline','').strip().lower()}|{r.get('direction','')}"
        if not key.strip("|"):
            continue
        prev = unique.get(key)
        if not prev:
            unique[key] = r
        else:
            has_prev_fee = bool(prev.get("fee"))
            has_new_fee = bool(r.get("fee"))
            if has_new_fee and not has_prev_fee:
                unique[key] = r
    for r in unique.values():
        if not r.get("date"):
            fee_url = r.get("url") or ""
            iso = _fetch_transfer_date(session, fee_url)
            if not iso and r.get("fee") and "/" in r["fee"]:
                iso = _to_iso(r["fee"].split()[-1])
            r["date"] = iso or datetime.now().date().isoformat()
    if not rows:
        print("[transfermarkt] Aucun transfert parsé", file=sys.stderr)
    df = pd.DataFrame(list(unique.values()) or rows)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_transfers_official.csv"
    df.to_csv(out_path, index=False)
    print(out_path)


if __name__ == "__main__":
    main()
