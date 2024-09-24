import aiohttp

async def get_rank_based_on_pp(pp):
    url = "https://osudaily.net/data/getPPRank.php?t=pp&v=" + \
          str(pp) + "&m=0"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
            return data


async def get_pp_based_on_rank(rank):
    url = "https://osudaily.net/data/getPPRank.php?t=rank&v=" + \
          str(rank) + "&m=0"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
            return data