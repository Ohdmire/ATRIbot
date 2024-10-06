from ATRIlib.TASKS.Jobs import multi_update_users_info_async,multi_update_users_bps_async
from ATRIlib.DB.Mongodb import db_bind,db_user
from ATRIlib.DB.pipeline_compress_score import remove_non_max_score_docs
from ATRIlib.DB.pipeline_shiftdatabase import pipeline_shiftdatabase
from ATRIlib.DB.pipeline_getgroupusers import get_group_users_id_list
import datetime

# 更新所有用户信息
async def job_update_all_user_info():
    all_bind_users = db_user.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['id'])

    raw = await multi_update_users_info_async(users_id_list)

    return raw

# 更新所有用户bps
async def job_update_all_user_bp():
    all_bind_users = db_user.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['id'])

    raw = await multi_update_users_bps_async(users_id_list)

    return raw

# 更新所有绑定用户信息
async def job_update_all_bind_user_info():
    all_bind_users = db_bind.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['user_id'])

    raw = await multi_update_users_info_async(users_id_list)

    return raw

# 更新所有绑定用户bps
async def job_update_all_bind_user_bps():
    all_bind_users = db_bind.find('')
    users_id_list = []

    for i in all_bind_users:
        users_id_list.append(i['user_id'])

    raw = await multi_update_users_bps_async(users_id_list)

    return raw

# 更新群里用户的bps
async def job_update_group_user_bps(group_id):
    
    users_id_list = get_group_users_id_list(group_id)

    raw = await multi_update_users_bps_async(users_id_list)

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