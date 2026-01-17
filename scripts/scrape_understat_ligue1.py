import asyncio
import os
import pandas as pd
from understat import Understat
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        us = Understat(session)
        table = await us.get_league_table("France", 2025)
        rows = []
        for t in table:
            team = t.get("title")
            team_id = t.get("id")
            team_data = await us.get_team(team_id, 2025)
            history = team_data.get("history", [])
            matches = len(history)
            xg = sum(float(h.get("xG", 0)) for h in history)
            xga = sum(float(h.get("xGA", 0)) for h in history)
            shots = sum(float(h.get("shots", 0)) for h in history)
            rows.append({
                "team": team,
                "matches": matches,
                "xg_total": xg,
                "xga_total": xga,
                "shots_total": shots
            })
        df = pd.DataFrame(rows)
        df["xg_per_match"] = df["xg_total"] / df["matches"].replace(0, pd.NA)
        df["xga_per_match"] = df["xga_total"] / df["matches"].replace(0, pd.NA)
        df["shots_per90"] = (df["shots_total"] / df["matches"].replace(0, pd.NA))
        out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "ligue1_team_advanced_stats.csv")
        df_out = df[["team", "shots_per90", "xg_per_match", "xga_per_match"]]
        df_out.to_csv(out_path, index=False)
        print(out_path)

if __name__ == "__main__":
    asyncio.run(main())
