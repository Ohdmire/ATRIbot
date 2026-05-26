from ATRIlib.DB.pipeline_medal import get_medal_list_from_db,get_user_medal_list_from_db,get_user_special_medal_list_from_db
from ATRIlib.DRAW.draw_medal import draw_medal_pr
from ATRIlib.DRAW.draw_medal_html import draw_medal_html
from ATRIlib.DB.Mongodb import db_medal,db_user
import aiohttp
import json
import re
from ATRIlib.TOOLS.Download import download_medal_async

OSEKAI_MEDALS_API = "https://inex.osekai.net/medals/"
OSEKAI_MEDAL_ASSET_BASE_URL = "https://inex.osekai.net/assets/osu/web"


def calculate_medal(medalid):

    medalstrct = get_medal_list_from_db(int(medalid))

    if not medalstrct:
        raise ValueError(f'无法在数据库中找到{medalid}的数据')

    raw = draw_medal_html(medalstrct[0])

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

async def calculate_special_medal(user_id):

    specialmedalprstrct = get_user_special_medal_list_from_db(user_id)

    pass_medal_Value = {
        55: "1",
        56: "2",
        57: "3",
        58: "4",
        59: "5",
        60: "6",
        61: "7",
        62: "8",
        242: "9",
        244: "10",
    }

    fc_medal_Value = {
        63: "1",
        64: "2",
        65: "3",
        66: "4",
        67: "5",
        68: "6",
        69: "7",
        70: "8",
        243: "9",
        245: "10",
    }
    
    result_pass_dict = {}
    result_fc_dict = {}

    for i in specialmedalprstrct:
        if i['achievement_id'] in pass_medal_Value:
            result_pass_dict[pass_medal_Value[i['achievement_id']]] = i['achieved_at']
        elif i['achievement_id'] in fc_medal_Value:
            result_fc_dict[fc_medal_Value[i['achievement_id']]] = i['achieved_at']

    return result_pass_dict,result_fc_dict

async def download_all_medals():
    async with aiohttp.ClientSession() as session:
        async with session.get(OSEKAI_MEDALS_API, timeout=aiohttp.ClientTimeout(total=60)) as response:
            response.raise_for_status()
            response_text = await response.text()

    match = re.search(r"const\s+medals_preload\s*=\s*(\{[\s\S]*?\});", response_text)
    if not match:
        raise ValueError("Osekai medals 页面中没有找到 medals_preload")
    payload = json.loads(match.group(1))

    medalstruct = payload.get("content")
    if not isinstance(medalstruct, list):
        raise ValueError("Osekai medals API 返回的数据中没有 content 列表")

    db_medal.drop()
    if medalstruct:
        db_medal.insert_many(medalstruct)

    medals_urls = []
    medals_ids = []

    for medal in medalstruct:
        link = medal["Link"]
        if not link.startswith(("http://", "https://")):
            link = f"{OSEKAI_MEDAL_ASSET_BASE_URL}/{link}"
        medals_urls.append(link)
        medals_ids.append(medal["Medal_ID"])

    await download_medal_async(medals_urls,medals_ids)

    return f"updated {len(medalstruct)} medals"
