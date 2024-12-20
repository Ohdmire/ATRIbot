from ATRIlib.DRAW.draw_profile import draw_profile
from ATRIlib.DB.Mongodb import db_user,db_yesterday

async def calculate_profile(user_id,is_yesterday=False):

    block_key_list = ["www.z4a.net"]

    userstruct = db_user.find_one({"id": user_id})

    username = userstruct["username"]
    avatar_url = userstruct["avatar_url"]
    html_content = userstruct["page"]["html"]
    raw_content = userstruct["page"]["raw"]

    # 检查是否出现敏感词
    for block_key in block_key_list:
        if block_key in raw_content:
            raise ValueError("该profile存在可疑网址，请检查")

    if is_yesterday:
        userstruct = db_yesterday.find_one({"user_id": user_id})
        if userstruct is not None:
            username = userstruct["user_data"]["username"]
            avatar_url = userstruct["user_data"]["avatar_url"]
            html_content = userstruct["user_data"]["page"]["html"]
        else:
            raise ValueError("未找到该玩家昨日数据")
        
    raw = await draw_profile(html_content, avatar_url, username,user_id)

    return raw