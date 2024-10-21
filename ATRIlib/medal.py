from ATRIlib.DB.pipeline_medal import get_medal_list_from_db,get_user_medal_list_from_db,get_user_special_medal_list_from_db
from ATRIlib.DRAW.draw_medal import draw_medal,draw_medal_pr
from ATRIlib.DB.Mongodb import db_medal,db_user
import re
from ATRIlib.TOOLS.Download import download_medal_async

def calculate_medal(medalid):

    medalstrct = get_medal_list_from_db(medalid)

    if not medalstrct:
        raise ValueError(f'无法在数据库中找到{medalid}的数据')

    medalstrctfix = medalstrct[0]

    # 去除标签
    pattern = re.compile(r'<[^>]+>', re.S)
    if medalstrctfix['instructions'] is not None:
        medalstrctfix['instructions'] = pattern.sub('', medalstrctfix['instructions'])

    if f'<i style="font-size:12px">' in medalstrctfix['solution_data']['solution']:
        medalstrctfix['solution_data']['solution_italic'] = medalstrctfix['solution_data']['solution'].split(f'<i style="font-size:12px">')[1].split(f'<i style="font-size:12px">')[0]
        medalstrctfix['solution_data']['solution'] = medalstrctfix['solution_data']['solution'].split(f'<i style="font-size:12px">')[0]

        medalstrctfix['solution_data']['solution'] = pattern.sub('', medalstrctfix['solution_data']['solution'])
        medalstrctfix['solution_data']['solution_italic'] = pattern.sub('', medalstrctfix['solution_data']['solution_italic'])


    raw = draw_medal(medalstrctfix)

    return raw

async def calculate_medal_pr(user_id):

    medalprstrct = get_user_medal_list_from_db(user_id)

    userstruct = db_user.find_one({'id': user_id})

    if not userstruct:
        raise ValueError(f'无法在数据库中找到{user_id}的数据')

    raw = await draw_medal_pr(medalprstrct,userstruct)

    return raw

async def calculate_uu_medal(user_id):

    specialmedalprstrct = get_user_special_medal_list_from_db(user_id)

    medal_Value = {
        55: "🟢1*Pass",
        56: "🟢2*Pass",
        57: "🟢3*Pass",
        58: "🟢4*Pass",
        59: "🟢5*Pass",
        60: "🟢6*Pass",
        61: "🟢7*Pass",
        62: "🟢8*Pass",
        242: "🟢9*Pass",
        244: "🟢10*Pass",
        63: "🟡1*FC",
        64: "🟡2*FC",
        65: "🟡3*FC",
        66: "🟡4*FC",
        67: "🟡5*FC",
        68: "🟡6*FC",
        69: "🟡7*FC",
        70: "🟡8*FC",
        243: "🟡9*FC",
        245: "🟡10*FC",
    }

    result_dict = {}

    for i in specialmedalprstrct:
        result_dict[medal_Value[i['achievement_id']]] = i['achieved_at']

    return result_dict


async def download_all_medals():

    medalstruct = db_medal.find('')

    medals_urls = []
    medals_ids =  []

    for i in medalstruct:
        medals_urls.append(i['link'])
        medals_ids.append(i['medalid'])

    raw = await download_medal_async(medals_urls,medals_ids)

    return raw
