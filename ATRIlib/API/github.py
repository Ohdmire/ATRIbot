import aiohttp
import re

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
        
async def get_latest_pprework_progress():

    filename = "news/2024/2024-10-28-performance-points-star-rating-updates.md"

    latest_commit_url = ""

    latest_commit_details = ""

    url = f"https://github.atri1024.help/repos/ppy/osu-wiki/commits?path={filename}"
    # 添加自定义请求头
    headers = {
        'Referer': 'https://ohdmire.github.io/',
        'Origin': 'https://ohdmire.github.io',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            latest_commit_url = (await response.json())[0]['url']

            # 把域名部分替换为github.atri1024.help
            latest_commit_url = replace_github_domain(latest_commit_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(latest_commit_url, headers=headers) as response:
            latest_commit_details = (await response.json())['files'][0]['patch']

    return latest_commit_details
        
def replace_github_domain(url: str) -> str:
    """
    替换任意域名为代理域名
    
    Args:
        url: 原始URL
    
    Returns:
        替换域名后的URL
    """
    # 匹配URL中的域名部分
    pattern = r'https?://[^/]+'
    
    # 替换为代理域名
    proxy_domain = 'https://github.atri1024.help'
    
    return re.sub(pattern, proxy_domain, url)
        
