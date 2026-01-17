print("=== SCRIPT MATCHES OL DEMARRE ===")

import requests
import pandas as pd
from io import StringIO
from pathlib import Path

CSV_URL = "https://fbref.com/en/squads/0d3c84b0/matchlogs/all_comps/matchlogs.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_PATH = Path("data/raw/ol_matches_raw.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

response = requests.get(CSV_URL, headers=HEADERS)
print("Status HTTP:", response.status_code)

if response.status_code != 200:
    raise Exception("FBref bloque l'accès (normal)")

csv_text = response.text
df = pd.read_csv(StringIO(csv_text))

df_ligue1 = df[df["Comp"] == "Ligue 1"]
df_ligue1.to_csv(OUTPUT_PATH, index=False)

print("OK - CSV créé :", OUTPUT_PATH)
