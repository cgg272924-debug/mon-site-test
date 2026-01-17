import asyncio
import aiohttp
from understat import Understat

async def main():
    async with aiohttp.ClientSession() as session:
        us = Understat(session)
        teams = await us.get_league_teams("France", 2025)
        print("Teams count:", len(teams))
        print("Sample team keys:", list(teams[0].keys()))
        team_id = teams[0].get("id")
        team_data = await us.get_team(team_id, 2025)
        print("Team data keys:", list(team_data.keys()))

if __name__ == "__main__":
    asyncio.run(main())
