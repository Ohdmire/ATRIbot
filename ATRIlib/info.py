from ATRIlib.API.PPYapiv2 import get_user_info,get_user_best_all_info
from ATRIlib.Manager.UserManager import update_user,update_bp


# 更新user信息 顺便返回user的id
async def update_user_info(osuname):
    userdata = await get_user_info(osuname)
    update_user(userdata)
    return userdata


# 更新bp信息
async def update_bp_info(user_id):
    bpdatas = await get_user_best_all_info(user_id)
    final_bp_data = update_bp(bpdatas)
    return final_bp_data