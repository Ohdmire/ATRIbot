from ATRIlib.API.OSUdaily import get_rank_based_on_pp,get_pp_based_on_rank

async def calculate_rank(pp):

    raw = await get_rank_based_on_pp(pp)

    return int(raw)

async def calculate_pp(rank):

    raw = await get_pp_based_on_rank(rank)

    return int(raw)
