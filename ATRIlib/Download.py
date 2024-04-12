import aiohttp
import asyncio
from pathlib import Path


class Downloader:

    def __init__(self):
        self.beatmaps_path = Path('./data/beatmaps/')
        self.semaphore = asyncio.Semaphore(5)

    async def get_beatmap_file(self, session, beatmap_id):
        file_path = self.beatmaps_path / f'{beatmap_id}.osu'
        url = f'https://osu.ppy.sh/osu/{beatmap_id}'
        async with self.semaphore:
            async with session.get(url) as response:
                with open(file_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

    async def download_files(self, beatmap_ids):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_beatmap_file(session, beatmap_id)
                     for beatmap_id in beatmap_ids]
            await asyncio.gather(*tasks)
