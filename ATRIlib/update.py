from ATRIlib.TOOLS import Download

async def update_user_avatar(user_id,avatar_url):
    try:
        await Download.download_avatar_async([avatar_url],[user_id])
        return "头像已更新"
    except:
        return "头像更新失败"