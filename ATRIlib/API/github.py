import aiohttp

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

async def get_latest_release():
    url = "https://api.github.com/repos/ppy/osu/releases/latest"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()
        
async def get_latest_pprework_progress():

    filename = "news/2024/2024-10-28-performance-points-star-rating-updates.md"

    latest_commit_url = ""

    latest_commit_details = ""

    url = url = f"https://api.github.com/repos/ppy/osu-wiki/commits?path={filename}"
    # 添加自定义请求头


    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            latest_commit_url = (await response.json())[0]['url']

    async with aiohttp.ClientSession() as session:
        async with session.get(latest_commit_url, headers=headers) as response:
            latest_commit_details = (await response.json())['files'][0]['patch']

    return latest_commit_details

async def get_news_url(index):

    index = -index

    url = f"https://api.github.com/repos/ppy/osu-wiki/contents/news/2025"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            commit_response = await response.json()
            commit_url = commit_response[index]['url']

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(commit_url, headers=headers) as response:
    #         commit_url_raw = (await response.json())['files'][0]['contents_url']
    #
    #         commit_url_raw = replace_github_domain_own(commit_url_raw)

    async with aiohttp.ClientSession() as session:
        async with session.get(commit_url, headers=headers) as response:

            markdown_obj = (await response.json())

            markdown_url = markdown_obj['download_url']
            markdown_name = markdown_obj['name'].split('.')[0]


            return markdown_url,markdown_name