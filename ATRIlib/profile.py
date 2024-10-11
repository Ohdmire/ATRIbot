from ATRIlib.DRAW.draw_profile import draw_profile
from ATRIlib.DB.Mongodb import db_user

async def calculate_profile(user_id):

    userstruct = db_user.find_one({"id": user_id})

    username = userstruct["username"]
    avatar_url = userstruct["avatar_url"]
    html_content = userstruct["page"]["html"]

    raw = await draw_profile(html_content, avatar_url, username,user_id)

    return raw