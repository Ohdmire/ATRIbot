import asyncio
from functools import wraps
import time

# 在文件顶部添加以下代码

def throttle(seconds=300):
    def decorator(func):
        last_run = 0
        running = False
        results = None

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_run, running, results

            current_time = time.time()
            if current_time - last_run < seconds:
                if running:
                    # 如果函数正在运行,等待它完成并返回结果
                    while running:
                        await asyncio.sleep(0.1)
                    return "success"
                elif results is not None:
                    # 如果在冷却时间内且有之前的结果,直接返回"success"
                    return "success"

            if not running:
                running = True
                last_run = current_time
                results = None
                try:
                    results = await func(*args, **kwargs)
                finally:
                    running = False

            return results

        return wrapper
    return decorator

from ATRIlib.TASKS.Jobs import multi_update_users_info_async,multi_update_users_bps_async,multi_update_beatmap_type
from ATRIlib.DB.Mongodb import db_bind,db_user
from ATRIlib.DB.pipeline_compress_score import remove_non_max_score_docs
from ATRIlib.DB.pipeline_shiftdatabase import pipeline_shiftdatabase
from ATRIlib.DB.pipeline_getgroupusers import get_group_users_id_list
from ATRIlib.DB.Mongodb import db_bp

import datetime

# 更新用户bp的beatmaptype
@throttle()
async def job_update_user_beatmap_type(user_id):

    bpinfo = db_bp.find_one({"id": user_id})

    bps_beatmap_id_list = bpinfo["bps_beatmapid"]

    raw = await multi_update_beatmap_type(bps_beatmap_id_list)

    return raw

# 更新所有用户信息
@throttle()
async def job_update_all_user_info():
    all_bind_users = db_user.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['id'])

    raw = await multi_update_users_info_async(users_id_list)

    return raw

# 更新所有用户bps
@throttle()
async def job_update_all_user_bp():
    all_bind_users = db_user.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['id'])

    raw = await multi_update_users_bps_async(users_id_list)

    return raw

# 更新所有绑定用户信息
@throttle()
async def job_update_all_bind_user_info():
    all_bind_users = db_bind.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['user_id'])

    raw = await multi_update_users_info_async(users_id_list)

    return raw

# 更新所有绑定用户bps
@throttle()
async def job_update_all_bind_user_bps():
    all_bind_users = db_bind.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['user_id'])

    raw = await multi_update_users_bps_async(users_id_list)

    return raw

# 更新群里用户的bps
@throttle()
async def job_update_group_user_bps(group_id):
    
    users_id_list = get_group_users_id_list(group_id)

    raw = await multi_update_users_bps_async(users_id_list)

    return raw

# 更新群里用户信息
@throttle()
async def job_update_group_user_info(group_id):

    users_id_list = get_group_users_id_list(group_id)

    raw = await multi_update_users_info_async(users_id_list)

    return raw

# 压缩score数据库
def job_compress_score_database():

    start_time = datetime.datetime.now()

    raw = remove_non_max_score_docs()

    end_time = datetime.datetime.now()

    dict = {}

    diff_time = end_time - start_time

    dict['diff_time'] = diff_time
    dict['count'] = raw

    return dict

# 转移数据库
def job_shift_database():

    raw = pipeline_shiftdatabase()

    return raw