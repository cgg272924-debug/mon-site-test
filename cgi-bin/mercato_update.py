import os
import sys
import json
from pathlib import Path

print("Content-Type: application/json")
print()

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

try:
    from scraping.ol_mercato_lequipe import main as run_scraper
except Exception as exc:
    print(json.dumps({"status": "error", "message": f"import failed: {exc}"}))
    raise SystemExit

try:
    run_scraper()
    out_path = root / "data" / "processed" / "ol_mercato.csv"
    exists = out_path.exists()
    print(json.dumps({"status": "ok", "csv_exists": exists, "csv": str(out_path)}))
except Exception as exc:
    print(json.dumps({"status": "error", "message": str(exc)}))
