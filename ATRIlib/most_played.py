from ATRIlib.API.PPYapiv2 import get_most_played_beatmaps
from ATRIlib.Manager.MostplayedManager import update_mostplayed
from ATRIlib.DB.Mongodb import db_user

async def get_most_played(user_id):

    played_count = db_user.find_one({'id': user_id})['beatmap_playcounts_count']

    raw = await get_most_played_beatmaps(user_id, played_count)

    # 创建一个列表来存储结果
    result_list = []

    # 遍历原始数据，构建所需的字典格式
    for beatmaps in raw:
        for beatmap in beatmaps:
            result_list.append({'beatmap_id': beatmap['beatmap_id'], 'count': beatmap['count']})

    update_mostplayed(user_id, result_list)

    return result_list

