import requests
import aiohttp
import asyncio
import functools
import logging
from ATRIlib.config import osuclientid, osuclientsecret

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_id = osuclientid
client_secret = osuclientsecret

# 获取访问令牌
token = None

# 定义一个全局信号量
semaphore = asyncio.Semaphore(1000)

def rate_limited(retries=3, delay=0.1, backoff=1):
    """
    Retry decorator with exponential backoff and rate limiting for async functions.

    Parameters:
    retries (int): Number of attempts.
    delay (int/float): Initial delay between attempts.
    backoff (int/float): Multiplier to increase the delay for each attempt.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            async with semaphore:
                while attempt < retries:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == retries - 1:
                            logger.error(f"Final attempt failed for {func.__name__} with args {args}, {kwargs}: {e}")
                            raise ValueError(f"API访问失败,请稍后再试")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff  # Increase delay time
                        attempt += 1
                        logger.warning(f"Retrying {func.__name__} due to {e}... Attempt {attempt + 1}")

        return wrapper

    return decorator

def get_token():
    global token
    url = 'https://osu.ppy.sh/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    response = requests.post(url, data=data)
    token = response.json()['access_token']

get_token()

@rate_limited()
async def get_user_info(osuname):
    url = f'https://osu.ppy.sh/api/v2/users/{osuname}/osu?key=username'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

@rate_limited()
async def get_user_info_fromid(osuid):
    url = f'https://osu.ppy.sh/api/v2/users/{osuid}/osu?key=id'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

@rate_limited()
async def get_user_best_all_info(user_id):
    url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/best?mode=osu&limit=100'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

@rate_limited()
async def get_user_scores_info(user_id, beatmap_id):
    url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores/users/{user_id}/all?mode=osu'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            try:
                data = data['scores']
            except:
                data = []
            return data

@rate_limited()
async def get_user_passrecent_info(user_id):
    url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/recent?mode=osu'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

@rate_limited()
async def get_beatmap_info(beatmap_id):
    url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

async def get_most_played_beatmaps(user_id, played_count):
    @rate_limited()
    async def fetch_most_played(session, url, params):
        headers = {'Authorization': f'Bearer {token}'}
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json()

    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, played_count, 100):
            url = f'https://osu.ppy.sh/api/v2/users/{user_id}/beatmapsets/most_played'
            params = {
                'mode': 'osu',
                'offset': i,
                'limit': 100,
            }
            result = await fetch_most_played(session, url, params)
            if result is not None:
                results.append(result)
    
    return results
