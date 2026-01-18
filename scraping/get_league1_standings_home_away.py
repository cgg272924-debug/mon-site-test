import pandas as pd
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup

print("=== RECUPERATION CLASSEMENT LIGUE 1 (DOMICILE/EXTERIEUR) ===")

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

MATCHES_FBREF_PATH = DATA_DIR / "ligue1_matches.csv"
RAW_OUTPUT = RAW_DIR / "ligue1_matches_raw.csv"

if MATCHES_FBREF_PATH.exists():
    source_path = MATCHES_FBREF_PATH
    mode = "fbref"
elif RAW_OUTPUT.exists():
    source_path = RAW_OUTPUT
    mode = "soccerdata"
else:
    source_path = None
    mode = "none"

if source_path is not None:
    print(f"Chargement des donnees depuis {source_path} ({'FBref' if mode == 'fbref' else 'soccerdata'})...")
    df_matches = pd.read_csv(source_path)
    print(f"OK - {len(df_matches)} lignes chargees")
else:
    print("AVERTISSEMENT: aucun fichier de matchs Ligue 1 trouve, bascule sur les classements externes")
    df_matches = pd.DataFrame()

# Fonction pour extraire le nom de l'équipe depuis match_report
def get_team_from_match(row):
    """Extrait le nom de l'équipe depuis match_report et venue"""
    match_report = str(row.get("match_report", ""))
    venue = row.get("venue", "")
    opponent = str(row.get("opponent", ""))
    
    if not match_report or match_report == "nan":
        return None
    
    TEAM_MAP = {
        "paris-saint-germain": "Paris Saint Germain",
        "paris-fc": "Paris FC",
        "le-havre": "Le Havre",
        "olympique-lyonnais": "Lyon",
        "lyon": "Lyon",
        "olympique-marseille": "Marseille",
        "marseille": "Marseille",
        "nice": "Nice",
        "lille": "Lille",
        "rennes": "Rennes",
        "strasbourg": "Strasbourg",
        "monaco": "Monaco",
        "nantes": "Nantes",
        "auxerre": "Auxerre",
        "metz": "Metz",
        "angers": "Angers",
        "lorient": "Lorient",
        "lens": "Lens",
        "toulouse": "Toulouse",
        "brest": "Brest",
    }

    def normalize_team_from_parts(parts):
        if not parts:
            return None
        # Essayer suffixes de longueur 3,2,1 pour ignorer les prefixes d'événement
        for k in range(min(3, len(parts)), 0, -1):
            candidate = "-".join(parts[-k:]).lower()
            if candidate in TEAM_MAP:
                return TEAM_MAP[candidate]
        # Sinon, tenter avec tout
        candidate_full = "-".join(parts).lower()
        if candidate_full in TEAM_MAP:
            return TEAM_MAP[candidate_full]
        # Dernier recours: dernier token capitalisé
        last = parts[-1].replace("-", " ").strip()
        if last:
            return last.title()
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
        # Supprimer un éventuel préfixe d'événement spécifique
        # Exemple connu: "Choc-des-Olympiques-"
        url_part = re.sub(r'^Choc-des-Olympiques-', '', url_part)
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
                team_norm = normalize_team_from_parts(team_parts)
                if team_norm:
                    return team_norm
        
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
                        t = normalize_team_from_parts(parts[:i]) or " ".join(parts[:i]).strip()
                        return t
                    else:
                        t = normalize_team_from_parts(parts[i:]) or " ".join(parts[i:]).strip()
                        return t
            
            # Si toujours pas trouvé, utiliser une séparation au milieu
            mid = len(parts) // 2
            if venue == "Home":
                t = normalize_team_from_parts(parts[:mid]) or " ".join(parts[:mid]).strip()
                return t
            else:
                t = normalize_team_from_parts(parts[mid:]) or " ".join(parts[mid:]).strip()
                return t
                
    except Exception as e:
        print(f"Erreur extraction equipe pour {match_report}: {e}")
        return None
    
    return None

def scrape_ligue1_official_standings():
    url = "https://ligue1.com/fr/competitions/ligue1mcdonalds/standings"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"AVERTISSEMENT: requete Ligue1.com echouee ({exc})")
        return pd.DataFrame()
    if resp.status_code != 200:
        print(f"AVERTISSEMENT: statut HTTP {resp.status_code} pour Ligue1.com")
        return pd.DataFrame()
    soup = BeautifulSoup(resp.text, "lxml")
    table = None
    for t in soup.find_all("table"):
        header_cells = t.find_all("th")
        headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]
        if not headers_text:
            continue
        if any("club" in h for h in headers_text) and any("pts" in h for h in headers_text):
            table = t
            break
    if table is None:
        debug_path = DATA_DIR / "processed" / "_debug_ligue1.html"
        try:
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            with debug_path.open("w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"AVERTISSEMENT: tableau classement introuvable sur Ligue1.com (HTML sauvegarde dans {debug_path})")
        except Exception as exc:
            print(f"AVERTISSEMENT: impossible de sauvegarder le HTML Ligue1.com ({exc})")
        return pd.DataFrame()
    header_cells = table.find_all("th")
    headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]
    col_idx = {}
    for idx, h in enumerate(headers_text):
        if "club" in h:
            col_idx["team"] = idx
        elif "j." in h or h.startswith("j " ) or h == "j" or "match" in h:
            col_idx["matches"] = idx
        elif "g-n-p" in h or "g-n" in h:
            col_idx["g_n_p"] = idx
        elif "pts" in h:
            col_idx["points"] = idx
        elif "but +" in h or "but+" in h or "bp" in h:
            col_idx["goals_for"] = idx
        elif "but -" in h or "but-" in h or "bc" in h:
            col_idx["goals_against"] = idx
        elif "diff" in h:
            col_idx["goal_difference"] = idx
    required = ["team", "matches", "points"]
    if any(k not in col_idx for k in required):
        return pd.DataFrame()
    def canonical_team(name: str) -> str:
        n = str(name or "").strip()
        mapping = {
            "paris saint-germain": "Paris Saint Germain",
            "paris sg": "Paris Saint Germain",
            "psg": "Paris Saint Germain",
            "olympique lyonnais": "Lyon",
            "ol": "Lyon",
            "olympique de marseille": "Marseille",
            "om": "Marseille",
        }
        key = n.lower()
        if key in mapping:
            return mapping[key]
        return n
    rows = []
    tbody = table.find("tbody") or table
    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells or len(cells) < len(header_cells):
            continue
        values = [c.get_text(" ", strip=True) for c in cells]
        try:
            team_raw = values[col_idx["team"]]
        except Exception:
            continue
        team = canonical_team(team_raw)
        def to_int_from_col(key):
            try:
                v = values[col_idx[key]]
                v = v.replace("\u00a0", " ").split()[0].replace(",", ".")
                v = "".join(ch for ch in v if (ch.isdigit() or ch in "+-"))
                if v == "" or v == "-":
                    return 0
                return int(v)
            except Exception:
                return 0
        matches = to_int_from_col("matches") if "matches" in col_idx else 0
        points = to_int_from_col("points")
        if points <= 0 and matches <= 0:
            continue
        goals_for = to_int_from_col("goals_for") if "goals_for" in col_idx else 0
        goals_against = to_int_from_col("goals_against") if "goals_against" in col_idx else 0
        if "goal_difference" in col_idx:
            gd = to_int_from_col("goal_difference")
        else:
            gd = goals_for - goals_against
        wins = draws = losses = 0
        if "g_n_p" in col_idx:
            try:
                triplet = values[col_idx["g_n_p"]]
                parts = triplet.replace("\u00a0", " ").split("-")
                if len(parts) == 3:
                    w, d, l = parts
                    wins = int(w)
                    draws = int(d)
                    losses = int(l)
            except Exception:
                pass
        ppm = round(points / matches, 2) if matches > 0 else 0.0
        rows.append(
            {
                "team": team,
                "matches": matches,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": gd,
                "points": points,
                "points_per_match": ppm,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False,
    ).reset_index(drop=True)
    df["rank"] = df.index + 1
    try:
        max_matches = pd.to_numeric(df["matches"], errors="coerce").max()
        print(f"[INFO] Classement Ligue1.com charge ({len(df)} equipes, max J={max_matches})")
    except Exception:
        print(f"[INFO] Classement Ligue1.com charge ({len(df)} equipes)")
    return df


def scrape_lequipe_standings():
    url = "https://www.lequipe.fr/Football/ligue-1/page-classement-equipes/general"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"AVERTISSEMENT: requete LEquipe echouee ({exc})")
        return pd.DataFrame()
    if resp.status_code != 200:
        print(f"AVERTISSEMENT: statut HTTP {resp.status_code} pour LEquipe")
        return pd.DataFrame()
    soup = BeautifulSoup(resp.text, "lxml")
    target_table = None
    for table in soup.find_all("table"):
        headers_row = table.find("thead")
        if not headers_row:
            continue
        header_cells = headers_row.find_all("th")
        headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]
        if not headers_text:
            continue
        if any("pts" in h for h in headers_text) and any("j" == h or "mj" in h for h in headers_text):
            target_table = table
            break
    if target_table is None:
        debug_path = DATA_DIR / "processed" / "_debug_lequipe.html"
        try:
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            with debug_path.open("w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"AVERTISSEMENT: tableau classement introuvable sur LEquipe (HTML sauvegarde dans {debug_path})")
        except Exception as exc:
            print(f"AVERTISSEMENT: impossible de sauvegarder le HTML LEquipe ({exc})")
        return pd.DataFrame()
    header_cells = target_table.find("thead").find_all("th")
    headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]
    col_idx = {}
    for idx, h in enumerate(headers_text):
        if "club" in h or "équipe" in h or "equipe" in h:
            col_idx["team"] = idx
        elif h in ("j", "mj") or "joue" in h:
            col_idx["matches"] = idx
        elif h.startswith("g") or "gagn" in h:
            col_idx["wins"] = idx
        elif h.startswith("n") or "nul" in h:
            col_idx["draws"] = idx
        elif h.startswith("p") or "perdu" in h:
            col_idx["losses"] = idx
        elif "bp" in h or "bp." in h or "bp " in h:
            col_idx["goals_for"] = idx
        elif "bc" in h or "bc." in h or "bc " in h:
            col_idx["goals_against"] = idx
        elif "diff" in h:
            col_idx["goal_difference"] = idx
        elif "pts" in h:
            col_idx["points"] = idx
    required = ["team", "matches", "wins", "draws", "losses", "goals_for", "goals_against", "points"]
    if any(k not in col_idx for k in required):
        print("AVERTISSEMENT: colonnes obligatoires manquantes dans le tableau LEquipe")
        return pd.DataFrame()
    def canonical_team(name):
        n = str(name or "").strip()
        mapping = {
            "paris-sg": "Paris Saint Germain",
            "paris sg": "Paris Saint Germain",
            "psg": "Paris Saint Germain",
            "le havre ac": "Le Havre",
            "le havre": "Le Havre",
            "ol": "Lyon",
            "ol lyon": "Lyon",
            "olympique lyonnais": "Lyon",
            "lyon": "Lyon",
            "olympique de marseille": "Marseille",
            "marseille": "Marseille",
        }
        key = n.lower()
        if key in mapping:
            return mapping[key]
        return n
    rows = []
    tbody = target_table.find("tbody")
    if not tbody:
        print("AVERTISSEMENT: tbody manquant dans le tableau LEquipe")
        return pd.DataFrame()
    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells or len(cells) < len(header_cells):
            continue
        values = [c.get_text(" ", strip=True) for c in cells]
        try:
            team_raw = values[col_idx["team"]]
        except Exception:
            continue
        team = canonical_team(team_raw)
        def to_int(idx_key):
            try:
                v = values[col_idx[idx_key]].replace("\u00a0", " ").split()[0].replace(",", ".")
                return int(float(v))
            except Exception:
                return 0
        matches = to_int("matches")
        wins = to_int("wins")
        draws = to_int("draws")
        losses = to_int("losses")
        goals_for = to_int("goals_for")
        goals_against = to_int("goals_against")
        points = to_int("points")
        if matches <= 0 and points <= 0:
            continue
        goal_difference = goals_for - goals_against
        ppm = round(points / matches, 2) if matches > 0 else 0.0
        rows.append(
            {
                "team": team,
                "matches": matches,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": goal_difference,
                "points": points,
                "points_per_match": ppm,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        print("AVERTISSEMENT: aucun enregistrement valide recupere depuis LEquipe")
        return df
    df = df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False,
    ).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def scrape_footmercato_standings():
    url = "https://www.footmercato.net/france/ligue-1/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"AVERTISSEMENT: requete FootMercato echouee ({exc})")
        return pd.DataFrame()
    if resp.status_code != 200:
        print(f"AVERTISSEMENT: statut HTTP {resp.status_code} pour FootMercato")
        return pd.DataFrame()
    soup = BeautifulSoup(resp.text, "lxml")

    target_table = None
    for table in soup.find_all("table"):
        header_row = table.find("thead")
        if not header_row:
            first_tr = table.find("tr")
            if not first_tr:
                continue
            header_cells = first_tr.find_all(["th", "td"])
        else:
            header_cells = header_row.find_all("th")
        headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]
        if not headers_text:
            continue
        if any("équipe" in h or "equipe" in h or "club" in h for h in headers_text) and any(
            h.strip() in ("j", "mj") or "match" in h for h in headers_text
        ):
            if any("pts" in h or "points" in h for h in headers_text):
                target_table = table
                break

    if target_table is None:
        print("AVERTISSEMENT: tableau classement introuvable sur FootMercato")
        return pd.DataFrame()

    header_row = target_table.find("thead")
    if header_row:
        header_cells = header_row.find_all("th")
    else:
        first_tr = target_table.find("tr")
        header_cells = first_tr.find_all(["th", "td"])
    headers_text = [h.get_text(" ", strip=True).lower() for h in header_cells]

    col_idx = {}
    for idx, h in enumerate(headers_text):
        if "équipe" in h or "equipe" in h or "club" in h:
            col_idx["team"] = idx
        elif h.strip() in ("j", "mj") or "match" in h:
            col_idx["matches"] = idx
        elif h.strip() in ("g", "v") or "vict" in h or "gagn" in h:
            col_idx["wins"] = idx
        elif h.strip() in ("n",) or "nul" in h:
            col_idx["draws"] = idx
        elif h.strip() in ("d", "p") or "perdu" in h:
            col_idx["losses"] = idx
        elif "bp" in h or "buts pour" in h or "bp " in h:
            col_idx["goals_for"] = idx
        elif "bc" in h or "buts contre" in h or "bc " in h:
            col_idx["goals_against"] = idx
        elif "dif" in h or "diff" in h:
            col_idx["goal_difference"] = idx
        elif "pts" in h or "points" in h:
            col_idx["points"] = idx

    required = ["team", "matches", "wins", "draws", "losses", "goals_for", "goals_against", "points"]
    if any(k not in col_idx for k in required):
        print("AVERTISSEMENT: colonnes obligatoires manquantes dans le tableau FootMercato")
        return pd.DataFrame()

    def canonical_team(name: str) -> str:
        n = str(name or "").strip()
        key = n.lower()
        mapping = {
            "paris sg": "Paris Saint Germain",
            "paris-sg": "Paris Saint Germain",
            "paris saint-germain": "Paris Saint Germain",
            "psg": "Paris Saint Germain",
            "olympique lyonnais": "Lyon",
            "ol lyon": "Lyon",
            "ol": "Lyon",
            "olympique de marseille": "Marseille",
            "om": "Marseille",
            "stade brestois 29": "Brest",
            "stade rennais fc": "Rennes",
            "losc lille": "Lille",
        }
        if key in mapping:
            return mapping[key]
        return n

    rows = []
    tbody = target_table.find("tbody") or target_table
    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        values = [c.get_text(" ", strip=True) for c in cells]
        if len(values) < len(headers_text):
            continue
        try:
            raw_team = values[col_idx["team"]]
        except Exception:
            continue
        team = canonical_team(raw_team)

        def to_int(idx_key: str) -> int:
            try:
                v = values[col_idx[idx_key]]
                v = re.sub(r"[^0-9\-\.]", "", v)
                if v in ("", "-"):
                    return 0
                return int(float(v))
            except Exception:
                return 0

        matches = to_int("matches")
        wins = to_int("wins")
        draws = to_int("draws")
        losses = to_int("losses")
        goals_for = to_int("goals_for")
        goals_against = to_int("goals_against")
        points = to_int("points")
        if matches <= 0 and points <= 0:
            continue
        if "goal_difference" in col_idx:
            try:
                gd = to_int("goal_difference")
            except Exception:
                gd = goals_for - goals_against
        else:
            gd = goals_for - goals_against
        ppm = round(points / matches, 2) if matches > 0 else 0.0
        rows.append(
            {
                "team": team,
                "matches": matches,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": gd,
                "points": points,
                "points_per_match": ppm,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        print("AVERTISSEMENT: aucun enregistrement valide recupere depuis FootMercato")
        return df
    df = df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False,
    ).reset_index(drop=True)
    df["venue"] = "All"
    try:
        max_matches = pd.to_numeric(df["matches"], errors="coerce").max()
        print(f"[INFO] Classement FootMercato charge ({len(df)} equipes, max J={max_matches})")
    except Exception:
        print(f"[INFO] Classement FootMercato charge ({len(df)} equipes)")
    return df


def scrape_maxifoot_standings():
    url = "https://m.maxifoot.fr/classement-ligue-1-france.htm"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"AVERTISSEMENT: requete Maxifoot echouee ({exc})")
        return pd.DataFrame()
    if resp.status_code != 200:
        print(f"AVERTISSEMENT: statut HTTP {resp.status_code} pour Maxifoot")
        return pd.DataFrame()
    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text("\n", strip=True)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    start_idx = None
    for idx, line in enumerate(lines):
        if line.startswith("Pos"):
            start_idx = idx
            break
    if start_idx is None:
        print("AVERTISSEMENT: en-tete de classement introuvable sur Maxifoot")
        return pd.DataFrame()
    data_lines = lines[start_idx + 1 :]
    def canonical_team(name: str) -> str:
        n = str(name or "").strip()
        key = n.lower()
        mapping = {
            "paris sg": "Paris Saint Germain",
            "paris-sg": "Paris Saint Germain",
            "paris saint-germain": "Paris Saint Germain",
            "psg": "Paris Saint Germain",
            "olympique lyonnais": "Lyon",
            "ol lyon": "Lyon",
            "ol": "Lyon",
            "olympique de marseille": "Marseille",
            "om": "Marseille",
            "stade brestois 29": "Brest",
            "stade rennais fc": "Rennes",
            "losc lille": "Lille",
        }
        if key in mapping:
            return mapping[key]
        return n

    rows = []
    i = 0
    while i + 9 < len(data_lines):
        pos_line = data_lines[i]
        if not pos_line.isdigit():
            i += 1
            continue
        pos = int(pos_line)
        if pos < 1 or pos > 20:
            i += 1
            continue
        team_raw = data_lines[i + 1]
        try:
            pts = int(data_lines[i + 2])
            matches = int(data_lines[i + 3])
            wins = int(data_lines[i + 4])
            draws = int(data_lines[i + 5])
            losses = int(data_lines[i + 6])
            goals_for = int(data_lines[i + 7])
            goals_against = int(data_lines[i + 8])
            goal_difference = int(data_lines[i + 9])
        except ValueError:
            i += 1
            continue
        team = canonical_team(team_raw)
        if matches <= 0 and pts <= 0:
            i += 10
            continue
        ppm = round(pts / matches, 2) if matches > 0 else 0.0
        rows.append(
            {
                "team": team,
                "matches": matches,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": goal_difference,
                "points": pts,
                "points_per_match": ppm,
            }
        )
        i += 10
    df = pd.DataFrame(rows)
    if df.empty:
        print("AVERTISSEMENT: aucun enregistrement valide recupere depuis Maxifoot")
        return df
    df = df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False,
    ).reset_index(drop=True)
    df["venue"] = "All"
    try:
        max_matches = pd.to_numeric(df["matches"], errors="coerce").max()
        print(f"[INFO] Classement Maxifoot charge ({len(df)} equipes, max J={max_matches})")
    except Exception:
        print(f"[INFO] Classement Maxifoot charge ({len(df)} equipes)")
    return df


def scrape_sportsmole_standings():
    url = "https://www.sportsmole.co.uk/football/ligue-1/table.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"AVERTISSEMENT: requete SportsMole echouee ({exc})")
        return pd.DataFrame()
    if resp.status_code != 200:
        print(f"AVERTISSEMENT: statut HTTP {resp.status_code} pour SportsMole")
        return pd.DataFrame()
    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")
    if not tables:
        print("AVERTISSEMENT: aucun tableau trouve sur SportsMole")
        return pd.DataFrame()

    def detect_table_title(tbl):
        h = tbl.find_previous(["h2", "h3", "h4", "h5"])
        if not h:
            return ""
        return h.get_text(" ", strip=True).lower()

    candidates = []
    for tbl in tables:
        header_row = tbl.find("thead")
        if header_row:
            header_cells = header_row.find_all("th")
        else:
            first_tr = tbl.find("tr")
            if not first_tr:
                continue
            header_cells = first_tr.find_all(["th", "td"])
        headers_text = [c.get_text(" ", strip=True).lower() for c in header_cells]
        if not headers_text:
            continue
        if not any("team" in h for h in headers_text):
            continue
        if not any(h in ("p", "pl", "played") or h.strip() == "p" for h in headers_text):
            continue
        title = detect_table_title(tbl)
        candidates.append((tbl, headers_text, title))

    if not candidates:
        print("AVERTISSEMENT: aucun tableau de classement valide sur SportsMole")
        return pd.DataFrame()

    table_types = {}
    for idx, (tbl, headers_text, title) in enumerate(candidates):
        t = ""
        if "home table" in title or "home" in title:
            t = "Home"
        elif "away table" in title or "away" in title:
            t = "Away"
        elif "overall" in title or "ligue 1 table" in title or "as it stands" in title:
            t = "All"
        table_types[idx] = t

    labels = ["All", "Home", "Away"]
    remaining = [i for i, t in table_types.items() if not t]
    for label in labels:
        if any(t == label for t in table_types.values()):
            continue
        if not remaining:
            break
        i = remaining.pop(0)
        table_types[i] = label

    rows = []

    def parse_table(tbl, venue_label):
        header_row = tbl.find("thead")
        if header_row:
            header_cells = header_row.find_all("th")
        else:
            first_tr = tbl.find("tr")
            if not first_tr:
                return
            header_cells = first_tr.find_all(["th", "td"])
        headers_text = [c.get_text(" ", strip=True).lower() for c in header_cells]
        col_idx = {}
        for idx, h in enumerate(headers_text):
            if "team" in h:
                col_idx["team"] = idx
            elif h in ("p", "pl", "played"):
                col_idx["matches"] = idx
            elif h in ("w", "won"):
                col_idx["wins"] = idx
            elif h in ("d", "draw", "drawn"):
                col_idx["draws"] = idx
            elif h in ("l", "lost", "losses"):
                col_idx["losses"] = idx
            elif h in ("f", "gf", "for"):
                col_idx["goals_for"] = idx
            elif h in ("a", "ga", "against"):
                col_idx["goals_against"] = idx
            elif "pts" in h or "points" in h:
                col_idx["points"] = idx
        required = ["team", "matches", "wins", "draws", "losses", "goals_for", "goals_against", "points"]
        if any(k not in col_idx for k in required):
            return
        tbody = tbl.find("tbody") or tbl
        for tr in tbody.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            values = [c.get_text(" ", strip=True) for c in cells]
            if len(values) < len(headers_text):
                continue
            try:
                team_raw = values[col_idx["team"]]
            except Exception:
                continue
            team = str(team_raw or "").strip()

            def to_int(idx_key):
                try:
                    v = values[col_idx[idx_key]]
                    v = re.sub(r"[^0-9\-\.]", "", v)
                    if v == "" or v == "-":
                        return 0
                    return int(float(v))
                except Exception:
                    return 0

            matches = to_int("matches")
            wins = to_int("wins")
            draws = to_int("draws")
            losses = to_int("losses")
            goals_for = to_int("goals_for")
            goals_against = to_int("goals_against")
            points = to_int("points")
            if matches <= 0 and points <= 0:
                continue
            goal_difference = goals_for - goals_against
            ppm = round(points / matches, 2) if matches > 0 else 0.0
            rows.append(
                {
                    "team": team,
                    "venue": venue_label,
                    "matches": matches,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "goal_difference": goal_difference,
                    "points": points,
                    "points_per_match": ppm,
                }
            )

    for idx, (tbl, headers_text, title) in enumerate(candidates):
        venue_label = table_types.get(idx) or ""
        if venue_label not in ("All", "Home", "Away"):
            continue
        parse_table(tbl, venue_label)

    df = pd.DataFrame(rows)
    if df.empty:
        print("AVERTISSEMENT: aucun enregistrement valide recupere depuis SportsMole")
        return df
    return df


def build_external_standings():
    df_ligue1 = scrape_ligue1_official_standings()
    if not df_ligue1.empty:
        df = df_ligue1.copy()
        df["venue"] = "All"
    else:
        df_maxi = scrape_maxifoot_standings()
        if not df_maxi.empty:
            df = df_maxi.copy()
        else:
            df_fm = scrape_footmercato_standings()
            if not df_fm.empty:
                df = df_fm.copy()
            else:
                df_sm = scrape_sportsmole_standings()
                if not df_sm.empty:
                    df = df_sm.copy()
                else:
                    df_leq = scrape_lequipe_standings()
                    if df_leq.empty:
                        return pd.DataFrame()
                    df = df_leq.copy()
                    df["venue"] = "All"
    for col in ["matches", "wins", "draws", "losses", "goals_for", "goals_against", "points"]:
        if col not in df.columns:
            return pd.DataFrame()
    if "goal_difference" not in df.columns:
        df["goal_difference"] = df["goals_for"] - df["goals_against"]
    if "points_per_match" not in df.columns:
        df["points_per_match"] = (df["points"] / df["matches"]).round(2)
    df["win_rate"] = (df["wins"] / df["matches"] * 100).round(1)
    df["goals_for_per_match"] = (df["goals_for"] / df["matches"]).round(2)
    df["goals_against_per_match"] = (df["goals_against"] / df["matches"]).round(2)
    if "venue" not in df.columns:
        df["venue"] = "All"
    df = df[[
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
        "goals_against_per_match",
    ]]
    df = df.sort_values(
        ["venue", "points", "goal_difference", "goals_for"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)
    df["rank"] = df.groupby("venue").cumcount() + 1
    return df


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

if mode == "fbref":
    if "home_team" not in df_matches.columns or "away_team" not in df_matches.columns or "score" not in df_matches.columns:
        print("ERREUR: Colonnes home_team, away_team ou score manquantes dans ligue1_matches.csv")
        exit(1)

    if "season" in df_matches.columns:
        seasons = sorted(str(s) for s in df_matches["season"].dropna().unique())
        if seasons:
            current_season = seasons[-1]
            df_matches = df_matches[df_matches["season"].astype(str) == current_season].copy()
            print(f"Saison utilisee: {current_season} ({len(df_matches)} lignes)")

    for idx, row in df_matches.iterrows():
        score = str(row.get("score", ""))
        parts = re.split(r"[-–]", score)
        if len(parts) != 2:
            continue
        try:
            home_goals = int(parts[0].strip())
            away_goals = int(parts[1].strip())
        except ValueError:
            continue

        home_team = str(row.get("home_team", "")).strip()
        away_team = str(row.get("away_team", "")).strip()
        if not home_team or not away_team:
            continue

        if home_goals > away_goals:
            home_result = "W"
            away_result = "L"
        elif home_goals == away_goals:
            home_result = "D"
            away_result = "D"
        else:
            home_result = "L"
            away_result = "W"

        for team, venue, gf, ga, result in [
            (home_team, "Home", home_goals, away_goals, home_result),
            (away_team, "Away", away_goals, home_goals, away_result),
        ]:
            points = get_points(result)

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

            standings_data.append({
                "team": team,
                "venue": venue,
                "matches": 1,
                "wins": 1 if result == "W" else 0,
                "draws": 1 if result == "D" else 0,
                "losses": 1 if result == "L" else 0,
                "goals_for": gf,
                "goals_against": ga,
                "points": points
            })
else:
    for idx, row in df_matches.iterrows():
        team = get_team_from_match(row)
        venue = row.get("venue", "")
        result = row.get("result", "")
        gf = pd.to_numeric(row.get("GF", 0), errors="coerce") or 0
        ga = pd.to_numeric(row.get("GA", 0), errors="coerce") or 0
        
        if not team or pd.isna(venue) or pd.isna(result):
            if idx < 5:
                print(f"Ligne {idx}: team={team}, venue={venue}, result={result}")
            continue
        
        points = get_points(result)
        
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
    print("AVERTISSEMENT: aucune donnee valide trouvee via les matchs, utilisation des classements externes")
    standings_agg = build_external_standings()
    if standings_agg.empty:
        print("ERREUR: impossible de construire le classement a partir des sources externes")
        exit(1)
else:
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

    standings_agg["goal_difference"] = standings_agg["goals_for"] - standings_agg["goals_against"]
    standings_agg["points_per_match"] = (standings_agg["points"] / standings_agg["matches"]).round(2)
    standings_agg["win_rate"] = (standings_agg["wins"] / standings_agg["matches"] * 100).round(1)
    standings_agg["goals_for_per_match"] = (standings_agg["goals_for"] / standings_agg["matches"]).round(2)
    standings_agg["goals_against_per_match"] = (standings_agg["goals_against"] / standings_agg["matches"]).round(2)

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

    standings_agg = standings_agg.sort_values(
        ["venue", "points", "goal_difference", "goals_for"],
        ascending=[True, False, False, False]
    ).reset_index(drop=True)

    standings_agg["rank"] = standings_agg.groupby("venue").cumcount() + 1

    external = build_external_standings()
    if not external.empty:
        external_all = external[external["venue"] == "All"]
        if not external_all.empty:
            external_all = external_all.drop_duplicates("team", keep="first")
            for col in [
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
                "goals_against_per_match",
            ]:
                mapping = external_all.set_index("team")[col]
                mask = (standings_agg["venue"] == "All") & standings_agg["team"].isin(mapping.index)
                standings_agg.loc[mask, col] = standings_agg.loc[mask, "team"].map(mapping)

    if external.empty:
        df_lequipe = scrape_lequipe_standings()
        if not df_lequipe.empty:
            stands_all = standings_agg[standings_agg["venue"] == "All"].copy()
            df_merged = stands_all.merge(
                df_lequipe,
                on="team",
                how="inner",
                suffixes=("_old", "_leq"),
            )
            if not df_merged.empty:
                for col in [
                    "matches",
                    "wins",
                    "draws",
                    "losses",
                    "goals_for",
                    "goals_against",
                    "goal_difference",
                    "points",
                    "points_per_match",
                ]:
                    standings_agg.loc[
                        standings_agg["team"].isin(df_merged["team"])
                        & (standings_agg["venue"] == "All"),
                        col,
                    ] = df_merged[f"{col}"]
                standings_agg_all = standings_agg[standings_agg["venue"] == "All"].copy()
                standings_agg_all = standings_agg_all.sort_values(
                    ["points", "goal_difference", "goals_for"],
                    ascending=False,
                ).reset_index(drop=True)
                standings_agg_all["rank"] = standings_agg_all.index + 1
                standings_agg = standings_agg.drop(
                    standings_agg[standings_agg["venue"] == "All"].index
                )
                standings_agg = pd.concat([standings_agg_all, standings_agg], ignore_index=True)

    teams = standings_agg["team"].dropna().unique()
    for team in teams:
        mask_all = (standings_agg["team"] == team) & (standings_agg["venue"] == "All")
        if not mask_all.any():
            continue
        row_all = standings_agg.loc[mask_all].iloc[0]
        has_home = ((standings_agg["team"] == team) & (standings_agg["venue"] == "Home")).any()
        has_away = ((standings_agg["team"] == team) & (standings_agg["venue"] == "Away")).any()
        if not has_home and not has_away:
            continue
        if not (pd.isna(row_all["matches"]) or pd.isna(row_all["points"]) or row_all["matches"] == 0):
            continue
        sub = standings_agg[
            (standings_agg["team"] == team)
            & (standings_agg["venue"].isin(["Home", "Away"]))
        ]
        if sub.empty:
            continue
        matches_sum = sub["matches"].sum()
        wins_sum = sub["wins"].sum()
        draws_sum = sub["draws"].sum()
        losses_sum = sub["losses"].sum()
        gf_sum = sub["goals_for"].sum()
        ga_sum = sub["goals_against"].sum()
        points_sum = sub["points"].sum()
        if matches_sum <= 0:
            continue
        gd = gf_sum - ga_sum
        ppm = round(points_sum / matches_sum, 2)
        win_rate = round(wins_sum / matches_sum * 100, 1)
        gfpm = round(gf_sum / matches_sum, 2)
        gapm = round(ga_sum / matches_sum, 2)
        standings_agg.loc[mask_all, "matches"] = matches_sum
        standings_agg.loc[mask_all, "wins"] = wins_sum
        standings_agg.loc[mask_all, "draws"] = draws_sum
        standings_agg.loc[mask_all, "losses"] = losses_sum
        standings_agg.loc[mask_all, "goals_for"] = gf_sum
        standings_agg.loc[mask_all, "goals_against"] = ga_sum
        standings_agg.loc[mask_all, "goal_difference"] = gd
        standings_agg.loc[mask_all, "points"] = points_sum
        standings_agg.loc[mask_all, "points_per_match"] = ppm
        standings_agg.loc[mask_all, "win_rate"] = win_rate
        standings_agg.loc[mask_all, "goals_for_per_match"] = gfpm
        standings_agg.loc[mask_all, "goals_against_per_match"] = gapm

    stands_all_final = standings_agg[standings_agg["venue"] == "All"].copy()
    stands_rest_final = standings_agg[standings_agg["venue"] != "All"].copy()
    stands_all_final = stands_all_final.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False,
    ).reset_index(drop=True)
    stands_all_final["rank"] = stands_all_final.index + 1
    standings_agg = pd.concat([stands_all_final, stands_rest_final], ignore_index=True)

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
