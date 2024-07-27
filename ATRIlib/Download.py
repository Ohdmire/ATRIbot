import aiohttp
import asyncio
from pathlib import Path

beatmaps_path = Path('./data/beatmaps/')
beatmaps_path_tmp = Path('./data/beatmaps_tmp/')
avatar_path = Path('./data/avatar/')
cover_path = Path('./data/cover/')
semaphore = asyncio.Semaphore(16)


async def get_beatmap_file(session, beatmap_id, Temp=True):
    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'
    url = f'https://osu.ppy.sh/osu/{beatmap_id}'
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                with open(file_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')


async def get_avatar_file(session, avatar_url, user_id):
    url = avatar_url
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                avatar_file = avatar_path / f'{user_id}.jpeg'
                with open(avatar_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')


async def download_osu_async(beatmap_ids, Temp=True):
    async with aiohttp.ClientSession() as session:
        tasks = [get_beatmap_file(session, beatmap_id, Temp)
                 for beatmap_id in beatmap_ids]
        await asyncio.gather(*tasks)


async def download_avatar_async(avatar_urls, user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [get_avatar_file(session, avatar_url, user_id)
                 for avatar_url, user_id in zip(avatar_urls, user_ids)]
        await asyncio.gather(*tasks)


async def download_cover(cover_url, beatmapset_id):
    url = cover_url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                cover_file = cover_path / f'{beatmapset_id}.jpg'
                with open(cover_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
