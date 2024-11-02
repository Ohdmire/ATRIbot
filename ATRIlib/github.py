from ATRIlib.API.github import get_latest_pprework_progress
from ATRIlib.DRAW.draw_commit import draw_commit

async def get_commit_content():
    details = await get_latest_pprework_progress()

    img_bytes = draw_commit(details)

    return img_bytes


    