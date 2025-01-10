from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.pp import calculate_bonus_pp,WEIGHT_LIST
import numpy as np
from ATRIlib.API.OSUdaily import get_rank_based_on_pp

# addpp
async def calculate_if_get_pp(user_id,pp_lists):

    # 获取bp的scoreid
    now_pp = db_user.find_one({'id': user_id})['statistics']['pp']

    bonuspp = calculate_bonus_pp(user_id)

    bp_pp_list = db_bp.find_one({'id': user_id})['bps_pp']

    new_pp_list = bp_pp_list.copy()

    for i in pp_lists:
        new_pp_list.append(i)

    sorted_new_pp_list = sorted(new_pp_list, reverse=True)[:100]

    list1 = np.array(sorted_new_pp_list)
    list2 = np.array(WEIGHT_LIST)
    list3 = list1 * list2

    new_pp_sum = np.sum(list3) + bonuspp

    # 获取变化的排名

    original_rank = db_user.find_one(
        {'id': user_id})['statistics']['global_rank']

    if new_pp_sum - now_pp > 1:
        try:
            new_rank = await get_rank_based_on_pp(new_pp_sum)
        except:
            new_rank = original_rank
    else:
        new_rank = original_rank

    raw={}

    raw["now_pp"] = now_pp
    raw["new_pp_sum"] = new_pp_sum
    raw["original_rank"] = original_rank
    raw["new_rank"] = new_rank

    return raw