
from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.TOOLS.Download import fetch_beatmap_file_async_all
from ATRIlib.pp import calculate_bonus_pp,calculate_iffcpp_one_in_bps,is_choke,WEIGHT_LIST
import numpy as np


# 计算choke pp
async def calculate_choke_pp(user_id):

    userstrct = db_user.find_one({'id': user_id})
    # 获取当前的pp
    mypp = userstrct['statistics']['pp']
    bpstruct = db_bp.find_one({'id': user_id})
    # 获取bp的scoreid
    bps_list = bpstruct['bps']
    # 获取bp的id
    bps_beatmapid_list = bpstruct['bps_beatmapid']
    # 获取bp的pp
    bps_pp_list = bpstruct['bps_pp']
    # 优化，先提前下载osu文件 方便后续update_if_fc_pp的时候不需要再去一个一个下载
    await fetch_beatmap_file_async_all(bps_beatmapid_list,Temp=False)

    # 判断choke
    fixedpp_list = []  # choke后如果fix的pp
    choke_dict = {} # choke损失的dict
    total_lost_pp_plus = 0
    total_lost_count = 0
    count = 0
    for bp in bps_list:
        # 更新pp_if_fc
        calculatedppstruct = await calculate_iffcpp_one_in_bps(user_id,count)
        iffcpp = calculatedppstruct["iffcpp"]
        lost_pp = bps_pp_list[count] - iffcpp
        if is_choke(user_id,count,calculatedppstruct['beatmapmaxcombo']) and lost_pp <-1:
            fixedpp_list.append(iffcpp)  # 更新之后的pplist
            total_lost_pp_plus += lost_pp
            choke_dict.update({count:lost_pp}) # 写入丢失的pp
            total_lost_count += 1
        else:
            fixedpp_list.append(bps_pp_list[count])  # 把原来的pp放入pplist
        count += 1

    # 获取整个fixed后的原始pp
    sorted_fixedpp_list = sorted(fixedpp_list,reverse=True)
    fixed_original_total_pp = np.array(sorted_fixedpp_list)
    list_weight = np.array(WEIGHT_LIST)
    weighted_fixed_original_total_pp = np.sum(fixed_original_total_pp * list_weight)
    bonuspp = calculate_bonus_pp(user_id)
    weighted_fixed_result_total_pp = weighted_fixed_original_total_pp + bonuspp

    total_lost_pp = mypp - weighted_fixed_result_total_pp

    raw = {}

    raw["mypp"] = mypp
    raw["weighted_fixed_result_total_pp"] = weighted_fixed_result_total_pp
    raw["total_lost_pp"] = total_lost_pp
    raw["total_lost_pp_plus"] = total_lost_pp_plus
    raw["total_lost_count"] = total_lost_count
    raw["choke_dict"] = choke_dict

    return raw
