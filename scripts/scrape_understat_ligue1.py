import asyncio
from pathlib import Path
from datetime import date

import aiohttp
import pandas as pd
from understat import Understat


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def detect_current_season() -> tuple[str, int]:
    path = DATA_DIR / "league1_standings_home_away.csv"
    if path.exists():
        try:
            df = pd.read_csv(path)
        except Exception:
            df = pd.DataFrame()
        if "season" in df.columns and not df.empty:
            seasons = df["season"].dropna().astype(str).unique().tolist()
            seasons = [s for s in seasons if s.strip()]
            if seasons:
                seasons_sorted = sorted(seasons)
                season_label = seasons_sorted[-1]
                parts = [p.strip() for p in season_label.split("-")]
                nums = [int(p) for p in parts if p.isdigit()]
                if nums:
                    season_year = min(nums)
                    return season_label, season_year
    year = date.today().year
    return f"{year-1}-{year}", year - 1


async def with_retry(coro_factory, retries: int = 3, delay: float = 1.0):
    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(delay)
    if last_exc is not None:
        raise last_exc
    return None


async def main() -> None:
    season_label, season_year = detect_current_season()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        us = Understat(session)
        table = await with_retry(
            lambda: us.get_league_table("ligue_1", season_year, with_headers=True)
        )
    out_dir = DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    adv_path = out_dir / "ligue1_team_advanced_stats.csv"
    profile_path = out_dir / "league1_understat_team_profiles.csv"
    if not table:
        if not adv_path.exists():
            pd.DataFrame(
                columns=[
                    "team",
                    "possession_pct",
                    "shots_per90",
                    "xg_per_match",
                    "xga_per_match",
                ]
            ).to_csv(adv_path, index=False)
        if not profile_path.exists():
            pd.DataFrame(
                columns=[
                    "season",
                    "team",
                    "matches",
                    "xg_total",
                    "xga_total",
                    "shots_total",
                    "deep_total",
                    "deep_allowed_total",
                    "field_tilt_avg",
                    "ppda_att_avg",
                    "ppda_def_avg",
                    "xg_per_match",
                    "xga_per_match",
                    "shots_per90",
                    "deep_per90",
                    "deep_allowed_per90",
                ]
            ).to_csv(profile_path, index=False)
        print(str(adv_path))
        return
    header = table[0]
    rows = table[1:]
    if not rows:
        if not adv_path.exists():
            pd.DataFrame(
                columns=[
                    "team",
                    "possession_pct",
                    "shots_per90",
                    "xg_per_match",
                    "xga_per_match",
                ]
            ).to_csv(adv_path, index=False)
        if not profile_path.exists():
            pd.DataFrame(
                columns=[
                    "season",
                    "team",
                    "matches",
                    "xg_total",
                    "xga_total",
                    "shots_total",
                    "deep_total",
                    "deep_allowed_total",
                    "field_tilt_avg",
                    "ppda_att_avg",
                    "ppda_def_avg",
                    "xg_per_match",
                    "xga_per_match",
                    "shots_per90",
                    "deep_per90",
                    "deep_allowed_per90",
                ]
            ).to_csv(profile_path, index=False)
        print(str(adv_path))
        return
    df = pd.DataFrame(rows, columns=header)
    df["team"] = df["Team"].astype(str)
    for col in ["M", "xG", "xGA", "PPDA", "OPPDA", "DC", "ODC"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        else:
            df[col] = 0.0
    matches = df["M"].astype(float)
    xg_total = df["xG"].astype(float)
    xga_total = df["xGA"].astype(float)
    deep_total = df["DC"].astype(float)
    deep_allowed_total = df["ODC"].astype(float)
    ppda_att = df["PPDA"].astype(float)
    ppda_def = df["OPPDA"].astype(float)
    denom = deep_total + deep_allowed_total
    field_tilt = pd.Series(0.0, index=df.index)
    mask = denom > 0
    field_tilt.loc[mask] = (deep_total[mask] / denom[mask]).astype(float)
    safe_matches = matches.where(matches > 0, 1.0)
    profiles = pd.DataFrame(
        {
            "season": season_label,
            "team": df["team"],
            "matches": matches,
            "xg_total": xg_total,
            "xga_total": xga_total,
            "shots_total": 0.0,
            "deep_total": deep_total,
            "deep_allowed_total": deep_allowed_total,
            "field_tilt_avg": field_tilt,
            "ppda_att_avg": ppda_att,
            "ppda_def_avg": ppda_def,
            "xg_per_match": xg_total / safe_matches,
            "xga_per_match": xga_total / safe_matches,
            "shots_per90": 0.0,
            "deep_per90": deep_total / safe_matches,
            "deep_allowed_per90": deep_allowed_total / safe_matches,
        }
    )
    profiles.to_csv(profile_path, index=False)
    df_adv = profiles.copy()
    df_adv["possession_pct"] = df_adv["field_tilt_avg"] * 100.0
    df_adv_out = df_adv[
        [
            "team",
            "possession_pct",
            "shots_per90",
            "xg_per_match",
            "xga_per_match",
        ]
    ]
    df_adv_out.to_csv(adv_path, index=False)
    print(str(adv_path))


if __name__ == "__main__":
    asyncio.run(main())
