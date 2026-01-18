import asyncio

import aiohttp
from understat import Understat


async def main() -> None:
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
        table = await us.get_league_table("ligue_1", 2025, with_headers=True)
        print("Rows in league_table:", len(table))
        header = table[0]
        first_team = table[1]
        print("Header row:", header)
        print("First team row:", first_team)


if __name__ == "__main__":
    asyncio.run(main())
