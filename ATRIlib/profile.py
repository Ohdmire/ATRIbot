from ATRIlib.DRAW.draw_profile import draw_profile
from ATRIlib.DB.Mongodb import db_user,db_yesterday

async def calculate_profile(user_id,is_yesterday=False):

    userstruct = db_user.find_one({"id": user_id})

    username = userstruct["username"]
    avatar_url = userstruct["avatar_url"]
    html_content = userstruct["page"]["html"]

    if is_yesterday:
        userstruct = db_yesterday.find_one({"id": user_id})
        if userstruct is not None:
            username = userstruct["user_data"]["username"]
            avatar_url = userstruct["user_data"]["avatar_url"]
            html_content = userstruct["user_data"]["page"]["html"]
        else:
            raise ValueError("未找到该玩家昨日数据")
        
    raw = await draw_profile(html_content, avatar_url, username,user_id)

    return raw