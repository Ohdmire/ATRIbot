import requests
import aiohttp
import asyncio
import functools
import logging
from ATRIlib.Config.config import pppclientid, pppclientsecret

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_id = pppclientid
client_secret = pppclientsecret

ppp_base_url = 'https://kanon-apis.desu.life:41000/lazybot'

# 获取访问令牌
token = None

# 定义headers
headers = {'Authorization': f'Bearer {token}'}

# 定义一个全局信号量
semaphore = asyncio.Semaphore(1000)


def rate_limited(retries=3, delay=1, backoff=1):
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
                            logger.error(
                                f"Final attempt failed for {func.__name__} with args:<{args}>\n kwargs:<{kwargs}>\n")
                            raise ValueError(f"API访问失败,请稍后再试")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff  # Increase delay time
                        attempt += 1
                        logger.warning(f"Retrying {func.__name__} due to {e}... Attempt {attempt + 1}")

        return wrapper

    return decorator


def get_token_ppp():
    global token, headers
    url = f'{ppp_base_url}/auth/token'
    data = {
        'clientId': client_id,
        'clientSecret': client_secret,
    }
    response = requests.post(url, data=data)
    token = response.json()['data']
    headers = {'Authorization': f'Bearer {token}'}


get_token_ppp()


@rate_limited()
async def get_user_ppp_info(user_id):
    url = f'{ppp_base_url}/player/info?id={user_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data