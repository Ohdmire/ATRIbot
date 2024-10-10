from ATRIlib.API.PPYapiv2 import get_most_played_beatmaps
from ATRIlib.Manager.MostplayedManager import update_mostplayed
from ATRIlib.DB.Mongodb import db_user

async def get_most_played(user_id):
    played_count = db_user.find_one({'id': user_id})['beatmap_playcounts_count']
    raw = await get_most_played_beatmaps(user_id, played_count)

    # 使用列表推导式替换原来的嵌套循环
    result_list = [{'beatmap_id': beatmap['beatmap_id'], 'count': beatmap['count']}
                   for beatmaps in raw
                   for beatmap in beatmaps]

    update_mostplayed(user_id, result_list)
    return result_list

