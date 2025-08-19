from ATRIlib.info import update_user_info,update_bp_info
from ATRIlib.bind import get_bpstruct_from_bind,get_userstrct_update_from_bind

# 能够返回userstruct
async def get_userstruct_automatically(qq_id, osuname,isOther=False):
    if osuname is None:
        userstruct = await get_userstrct_update_from_bind(qq_id,isOther) # 不手动输入name的情况，从bind数据库中获取userstruct(还是要更新)
    else:
        userstruct = await update_user_info(osuname) # 否则fallback到osuname 去官网更新写入数据库后返回userstruct
    if userstruct is None:
        raise ValueError("无法获取用户信息，请稍候重试")
    return userstruct

# 强制返回一个bpstruct
async def get_bpstruct(user_id):
    bpstruct = await update_bp_info(user_id)
    if bpstruct is None:
        raise ValueError("无法获取用户bp信息，请稍候重试")
    return bpstruct