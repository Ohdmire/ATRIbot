import aiohttp

async def get_latest_release():
    url = "https://github.atri1024.help/repos/ppy/osu/releases/latest"
    # 添加自定义请求头
    headers = {
        'Referer': 'https://ohdmire.github.io/',
        'Origin': 'https://ohdmire.github.io',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()