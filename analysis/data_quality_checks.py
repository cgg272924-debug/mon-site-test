import pandas as pd
from pathlib import Path


class DatasetInfo:
    def __init__(self, name, path, key_cols=None, date_cols=None):
        self.name = name
        self.path = Path(path)
        self.key_cols = key_cols or []
        self.date_cols = date_cols or []


DATASETS = [
    DatasetInfo(
        "ol_match_score_final",
        "data/processed/ol_match_score_final.csv",
        key_cols=["date", "opponent"],
        date_cols=["date"],
    ),
    DatasetInfo(
        "league1_standings_home_away",
        "data/processed/league1_standings_home_away.csv",
        key_cols=["team"],
    ),
    DatasetInfo(
        "ol_player_minutes",
        "data/processed/ol_player_minutes.csv",
        key_cols=["season", "game_id", "player"],
    ),
    DatasetInfo(
        "ol_players_rated",
        "data/processed/ol_players_rated.csv",
        key_cols=["player"],
    ),
    DatasetInfo(
        "ol_injuries_transfermarkt",
        "data/processed/ol_injuries_transfermarkt.csv",
        key_cols=["player"],
    ),
    DatasetInfo(
        "ol_lineups_by_match",
        "data/processed/ol_lineups_by_match.csv",
        key_cols=["match_key", "player"],
    ),
    DatasetInfo(
        "ol_match_proba_dataset",
        "data/processed/ol_match_proba_dataset.csv",
        key_cols=["match_key"],
        date_cols=["date"],
    ),
    DatasetInfo(
        "ol_player_impact_scores",
        "data/processed/ol_player_impact_scores.csv",
        key_cols=["name"],
    ),
    DatasetInfo(
        "ol_player_match_impact",
        "data/processed/ol_player_match_impact.csv",
        key_cols=["player"],
    ),
    DatasetInfo(
        "ol_next_match_simulation",
        "data/processed/ol_next_match_simulation.csv",
        key_cols=["opponent", "venue"],
    ),
    DatasetInfo(
        "match_lookup",
        "data/processed/match_lookup.csv",
        key_cols=["match_key"],
        date_cols=["date"],
    ),
]


def check_dataset(info: DatasetInfo) -> None:
    print(f"=== {info.name} ===")
    if not info.path.exists():
        print(f"status=missing path={info.path}")
        return
    try:
        df = pd.read_csv(info.path)
    except Exception as exc:
        print(f"status=error path={info.path} error={exc}")
        return

    rows, cols = df.shape
    print(f"status=ok path={info.path} rows={rows} cols={cols}")

    missing_per_col = df.isna().sum()
    total_missing = int(missing_per_col.sum())
    print(f"missing_total={total_missing}")
    if total_missing > 0:
        missing_summary = {
            col: int(count)
            for col, count in missing_per_col.items()
            if int(count) > 0
        }
        print(f"missing_by_col={missing_summary}")

    if info.key_cols:
        for col in info.key_cols:
            if col not in df.columns:
                print(f"key_column_missing={col}")
        present_keys = [c for c in info.key_cols if c in df.columns]
        if present_keys:
            dup_count = int(df.duplicated(subset=present_keys).sum())
            print(f"duplicates_on_key={dup_count} key={present_keys}")

    for col in info.date_cols:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            invalid = int(parsed.isna().sum())
            if invalid > 0:
                print(f"invalid_dates[{col}]={invalid}")
            valid = parsed.dropna()
            if not valid.empty:
                min_date = valid.min().date()
                max_date = valid.max().date()
                print(f"date_range[{col}]={min_date}..{max_date}")


def main() -> None:
    for info in DATASETS:
        check_dataset(info)


if __name__ == "__main__":
    main()

