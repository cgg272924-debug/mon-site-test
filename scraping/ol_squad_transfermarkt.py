from datetime import date
from pathlib import Path

import pandas as pd

from app.services.clubs.players import TransfermarktClubPlayers


CLUB_ID = "1041"


def main() -> None:
    today = date.today()
    season_year = today.year if today.month >= 7 else today.year - 1
    season_id = str(season_year)
    tfmkt = TransfermarktClubPlayers(club_id=CLUB_ID, season_id=season_id)
    data = tfmkt.get_club_players()
    players = data.get("players", [])
    df = pd.DataFrame(players)
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_squad_transfermarkt.csv"
    df.to_csv(out_path, index=False)
    print(out_path)


if __name__ == "__main__":
    main()

