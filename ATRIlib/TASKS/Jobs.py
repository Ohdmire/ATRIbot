import asyncio
import functools
import logging
import time

from ATRIlib.API.PPYapiv2 import get_user_info_fromid,get_user_best_all_info,get_user_scores_info
from ATRIlib.Manager.UserManager import update_user,update_bp
from ATRIlib.Manager.ScoreManager import update_score_many

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义一个全局信号量
semaphore = asyncio.Semaphore(100)


def rate_limited(retries=3, delay=1, backoff=2):
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
                            return None
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff  # Increase delay time
                        attempt += 1
                        logger.warning(f"Retrying {func.__name__} due to {e}... Attempt {attempt + 1}")

        return wrapper

    return decorator


@rate_limited()
async def single_update_user(osuid):
    userdata = await get_user_info_fromid(osuid)
    update_user(userdata)
    return userdata['id']


@rate_limited()
async def single_update_user_bps(osuid):
    bpdata = await get_user_best_all_info(osuid)
    update_bp(bpdata)
    return True


@rate_limited()
async def single_update_score(osuid, beatmap_id):
    scoredatas = await get_user_scores_info(osuid, beatmap_id)
    update_score_many(beatmap_id,scoredatas)
    return beatmap_id # 返回beatmap_id?


async def multi_update_users_info_async(users_id_lists):
    total_users = len(users_id_lists)
    start_time = time.time()

    tasks = [single_update_user(user_id) for user_id in users_id_lists]
    result = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    success_users = sum(1 for res in result if res is not None)

    fail_count = total_users - success_users

    result_text = f'共遍历{total_users}个用户info'

    if fail_count != 0:
        result_text += f'\n失败{fail_count}个'
    else:
        result_text += f'\n全部成功'

    result_text += f'\n用时{total_time}s'

    return result_text


async def multi_update_users_bps_async(users_id_lists):
    total_users = len(users_id_lists)
    start_time = time.time()

    tasks = [single_update_user_bps(user_id) for user_id in users_id_lists]
    result = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    success_users = sum(1 for res in result if res is not None)

    fail_count = total_users - success_users

    result_text = f'共遍历{total_users}个用户bp'

    if fail_count != 0:
        result_text += f'\n失败{fail_count}个'
    else:
        result_text += f'\n全部成功'

    result_text += f'\n用时{total_time}s'

    return result_text


async def multi_update_users_beatmap_score_async(beatmap_id, users_lists):
    total_users = len(users_lists)
    start_time = time.time()

    tasks = [single_update_score(user,beatmap_id) for user in users_lists]
    result = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    success_users = sum(1 for res in result if res is not None)

    fail_count = total_users - success_users

    result_text = f'共遍历{total_users}个用户score'

    if fail_count != 0:
        result_text += f'\n失败{fail_count}个'
    else:
        result_text += f'\n全部成功'

    result_text += f'\n用时{total_time}s'

    return result_text
