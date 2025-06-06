import numpy as np
from pathlib import Path

from ATRIlib.DB.Mongodb import db_bp,db_user,db_score
from ATRIlib.PP.Rosu import calculate_pp_if_all
from ATRIlib.TOOLS.Download import fetch_beatmap_file_async_one


WEIGHT_LIST = [1.0, 0.95, 0.9025, 0.8573749999999998, 0.8145062499999999, 0.7737809374999998, 0.7350918906249998, 0.6983372960937497, 0.6634204312890623, 0.6302494097246091, 0.5987369392383787, 0.5688000922764597, 0.5403600876626367, 0.5133420832795048, 0.4876749791155295, 0.46329123015975304, 0.44012666865176536, 0.4181203352191771, 0.3972143184582182, 0.3773536025353073, 0.3584859224085419, 0.34056162628811476, 0.323533544973709, 0.3073568677250236, 0.2919890243387724, 0.27738957312183377, 0.26352009446574204, 0.2503440897424549, 0.23782688525533216, 0.22593554099256555, 0.21463876394293727, 0.2039068257457904, 0.19371148445850087, 0.18402591023557582, 0.174824614723797, 0.16608338398760714, 0.1577792147882268, 0.14989025404881545, 0.14239574134637467, 0.13527595427905592, 0.12851215656510312, 0.12208654873684796, 0.11598222130000556, 0.11018311023500528, 0.10467395472325501, 0.09944025698709226, 0.09446824413773763, 0.08974483193085075, 0.0852575903343082, 0.0809947108175928, 0.07694497527671315, 0.07309772651287749,0.06944284018723361, 0.06597069817787193, 0.06267216326897833, 0.05953855510552941, 0.056561627350252934, 0.053733545982740286, 0.051046868683603266, 0.048494525249423104, 0.046069798986951946, 0.043766309037604346, 0.041577993585724136, 0.03949909390643792, 0.03752413921111602, 0.03564793225056022, 0.033865535638032206, 0.03217225885613059, 0.030563645913324066, 0.029035463617657863, 0.027583690436774964, 0.026204505914936217, 0.024894280619189402, 0.023649566588229934, 0.02246708825881844, 0.02134373384587751, 0.020276547153583634, 0.01926271979590445, 0.01829958380610923, 0.017384604615803767, 0.01651537438501358, 0.0156896056657629, 0.014905125382474753, 0.014159869113351013, 0.013451875657683464, 0.012779281874799289, 0.012140317781059324, 0.011533301892006359, 0.01095663679740604, 0.010408804957535737, 0.00988836470965895, 0.009393946474176, 0.008924249150467202, 0.00847803669294384, 0.008054134858296648, 0.007651428115381815, 0.007268856709612724, 0.006905413874132088, 0.006560143180425483, 0.006232136021404208]
beatmaps_path = Path('./data/beatmaps/')
beatmaps_path_tmp = Path('./data/beatmaps_tmp/')

# 计算原始pp
def calculate_origin_pp(user_id):
    bps_pplist = db_bp.find_one({'id': user_id})['bps_pp']

    if len(bps_pplist) < 100:
        bps_pplist = bps_pplist + [0] * (100 - len(bps_pplist))

    list1 = np.array(bps_pplist)
    list2 = np.array(WEIGHT_LIST)
    list3 = list1 * list2

    origin_pp_sum = np.sum(list3)

    return origin_pp_sum


# 计算bonus pp
def calculate_bonus_pp(user_id):
    # 获取bp的scoreid
    origin_pp = calculate_origin_pp(user_id)
    now_pp = db_user.find_one({'id': user_id})['statistics']['pp']
    bonus_pp = now_pp - origin_pp
    return bonus_pp


# 计算pp_if_fc
async def calculate_iffcpp_one_in_bps(user_id,count):

    bpstruct = db_bp.find_one({'id': user_id})

    beatmap_id = bpstruct['bps_beatmapid'][count]
    mods = bpstruct['bps_mods'][count]
    acc = bpstruct['bps_acc'][count] * 100
    # 获取osu文件来计算
    await fetch_beatmap_file_async_one(beatmap_id, Temp=False)
    # 不需要combo计算
    ppresult = await calculate_pp_if_all(beatmap_id, mods, acc, None, Temp=False)
    iffcpp = ppresult["fcpp"]
    maxcombo = ppresult["maxcombo"]
    raw={}
    raw["iffcpp"] = iffcpp
    raw["beatmapmaxcombo"] = maxcombo

    return raw

# 判断是否choke

def is_choke(user_id,count,beatmap_maxcombo):
    bpstruct = db_bp.find_one({'id': user_id})
    maxcombo = bpstruct["bps_maxcombo"][count]
    try:
        misscount = bpstruct["bps_statistics"][count]["miss"]
    except:
        misscount = 0
    if misscount/beatmap_maxcombo <= 0.002 and maxcombo > beatmap_maxcombo / 2 or misscount ==0 and (beatmap_maxcombo - maxcombo)/beatmap_maxcombo > 0.05:
        return True
    else:
        return False
