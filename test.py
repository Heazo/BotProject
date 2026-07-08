import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.telegram.org") as resp:
            print(resp.status)

asyncio.run(test())