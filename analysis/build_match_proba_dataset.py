from pathlib import Path
from typing import Dict

import pandas as pd


DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"


def load_csv(path: Path, required: bool = True) -> pd.DataFrame:
    if not path.exists():
        if required:
            raise FileNotFoundError(str(path))
        return pd.DataFrame()
    return pd.read_csv(path)


def canonical_team_name(name: str) -> str:
    return " ".join(name.lower().replace("-", " ").split())


def add_h2h_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)
    h2h_cols = [
        "h2h5_win_rate",
        "h2h5_draw_rate",
        "h2h5_loss_rate",
        "h2h10_win_rate",
        "h2h10_draw_rate",
        "h2h10_loss_rate",
        "h2h15_win_rate",
        "h2h15_draw_rate",
        "h2h15_loss_rate",
        "h2h_matches_played",
    ]
    for col in h2h_cols:
        df[col] = 0.0
    for idx, row in df.iterrows():
        opp = row["opponent"]
        current_date = row["date"]
        history = df[(df["opponent"] == opp) & (df["date"] < current_date)]
        history = history.sort_values("date")
        df.loc[idx, "h2h_matches_played"] = float(len(history))

        def compute_rates(n: int) -> Dict[str, float]:
            subset = history.tail(n)
            if subset.empty:
                return {"w": 0.0, "d": 0.0, "l": 0.0}
            total = float(len(subset))
            w = float((subset["result"] == "W").sum()) / total
            d = float((subset["result"] == "D").sum()) / total
            l = float((subset["result"] == "L").sum()) / total
            return {"w": w, "d": d, "l": l}

        r5 = compute_rates(5)
        r10 = compute_rates(10)
        r15 = compute_rates(15)
        df.loc[idx, "h2h5_win_rate"] = r5["w"]
        df.loc[idx, "h2h5_draw_rate"] = r5["d"]
        df.loc[idx, "h2h5_loss_rate"] = r5["l"]
        df.loc[idx, "h2h10_win_rate"] = r10["w"]
        df.loc[idx, "h2h10_draw_rate"] = r10["d"]
        df.loc[idx, "h2h10_loss_rate"] = r10["l"]
        df.loc[idx, "h2h15_win_rate"] = r15["w"]
        df.loc[idx, "h2h15_draw_rate"] = r15["d"]
        df.loc[idx, "h2h15_loss_rate"] = r15["l"]
    return df


def build_rivalry_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    total_by_opp = df.groupby("opponent")["date"].count().to_dict()
    manual_boost: Dict[str, float] = {
        "paris saint-germain": 0.8,
        "marseille": 0.8,
        "saint-etienne": 0.9,
    }
    values = []
    for _, row in df.iterrows():
        opp = row["opponent"]
        total = float(total_by_opp.get(opp, 0))
        base = min(1.0, total / 10.0)
        boosted = max(base, manual_boost.get(opp, 0.0))
        values.append(boosted)
    df["rivalry_index"] = values
    return df


def add_standings_features(df: pd.DataFrame, standings_path: Path) -> pd.DataFrame:
    df = df.copy()
    standings = load_csv(standings_path)
    standings = standings.copy()
    standings["team_key"] = standings["team"].astype(str).map(canonical_team_name)
    df["opponent_key"] = df["opponent"].astype(str).map(canonical_team_name)
    lyon_key = canonical_team_name("Lyon")
    lyon_row = standings[standings["team_key"] == lyon_key]
    if lyon_row.empty:
        raise RuntimeError("Lyon introuvable dans league1_standings_home_away.csv")
    lyon_row = lyon_row.iloc[0]
    df = df.merge(
        standings.add_prefix("opp_"),
        left_on="opponent_key",
        right_on="opp_team_key",
        how="left",
    )
    df["ol_rank"] = float(lyon_row["rank"])
    df["ol_home_rank"] = float(lyon_row["home_rank"])
    df["ol_away_rank"] = float(lyon_row["away_rank"])
    df["opp_rank"] = df["opp_rank"].astype(float)
    df["rank_diff"] = df["opp_rank"] - df["ol_rank"]
    df["opp_home_rank"] = df["opp_home_rank"].astype(float)
    df["opp_away_rank"] = df["opp_away_rank"].astype(float)
    return df


def add_context_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_home"] = (df["venue"] == "Home").astype(int)
    df["is_away"] = (df["venue"] == "Away").astype(int)
    df["result_points"] = df["points"].astype(float)
    return df


def main() -> None:
    base_path = PROCESSED_DIR / "ol_matches_with_match_key.csv"
    standings_path = PROCESSED_DIR / "league1_standings_home_away.csv"
    df_all = load_csv(base_path)
    df_all["date"] = pd.to_datetime(df_all["date"], errors="coerce")
    df_all = df_all.sort_values("date").reset_index(drop=True)
    df_lyon = df_all[df_all["opponent"].str.lower() != "lyon"].copy()
    df_lyon = add_h2h_features(df_lyon)
    df_lyon = build_rivalry_index(df_lyon)
    df_lyon = add_standings_features(df_lyon, standings_path)
    df_lyon = add_context_features(df_lyon)
    out_dir = PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ol_match_proba_dataset.csv"
    df_lyon.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Fichier créé: {out_path}")


if __name__ == "__main__":
    main()

