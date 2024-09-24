from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.DB.pipeline_pttpp import get_avgpp_pttpp_from_db
from ATRIlib.TOOLS.Mtools import leastsquares

def calculate_ptt_pp(user_id,pp_range): #pp_range暂时没有用了

    now_pp = db_user.find_one({'id': user_id})['statistics']['pp']

    now_bp1 = db_bp.find_one({'id': user_id})['bps_pp'][0]

    raw_users = get_avgpp_pttpp_from_db(user_id,pp_range)

    k2_bp2_list = []
    k2_pp_list = []

    for user in raw_users:
        try:
            k2_bp2_list.append(user['bp2pp'])
            k2_pp_list.append(user['statistics']['pp'])
        except:
            pass

    k2, b2 = leastsquares(k2_bp2_list, k2_pp_list)

    bps_ptt_pp = k2 * now_bp1 + b2

    raw={}

    raw['now_pp'] = now_pp
    raw['ptt_pp'] = bps_ptt_pp

    return raw