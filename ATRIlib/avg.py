from ATRIlib.DB.Mongodb import db_user
import numpy as np
from ATRIlib.DB.pipeline_avg import get_avgpp_list_from_db,get_avgpt_list_from_db,get_avgtth_list_from_db

#avgpp

def calculate_avg_pp(user_id, pp_range):

    result = get_avgpp_list_from_db(user_id, pp_range)

    return result

def calculate_avg_pt(user_id, pt_range):

    result = get_avgpt_list_from_db(user_id, pt_range)

    return result

def calculate_avg_tth(user_id, tth_range):

    result = get_avgtth_list_from_db(user_id, tth_range)

    return result

def calculate_avg_pp_back(user_id, pp_range):
    # 处理一下pp_range
    now_pp = db_user.find_one({'id': user_id})['statistics']['pp']
    start_pp = now_pp - pp_range
    end_pp = now_pp + pp_range

    range_users = db_user.find(
        {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

    bp1_pps_list = []
    bp2_pps_list = []
    bp3_pps_list = []
    bp4_pps_list = []
    bp5_pps_list = []
    bp100_pps_list = []

    for range_user in range_users:

        try:
            bp1_pps_list.append(range_user['bps_pp'][0])
            bp2_pps_list.append(range_user['bps_pp'][1])
            bp3_pps_list.append(range_user['bps_pp'][2])
            bp4_pps_list.append(range_user['bps_pp'][3])
            bp5_pps_list.append(range_user['bps_pp'][4])
            bp100_pps_list.append(range_user['bps_pp'][99])
        except:
            pass

    # 随便找个list计数
    users_amount = len(bp1_pps_list)

    avgbp1 = np.mean(bp1_pps_list)
    avgbp2 = np.mean(bp2_pps_list)
    avgbp3 = np.mean(bp3_pps_list)
    avgbp4 = np.mean(bp4_pps_list)
    avgbp5 = np.mean(bp5_pps_list)
    avgbp100 = np.mean(bp100_pps_list)

    user_origin_bps_pp = db_user.find_one({'id': user_id})['bps_pp']

    user_origin_bp1 = user_origin_bps_pp[0]
    user_origin_bp2 = user_origin_bps_pp[1]
    user_origin_bp3 = user_origin_bps_pp[2]
    user_origin_bp4 = user_origin_bps_pp[3]
    user_origin_bp5 = user_origin_bps_pp[4]
    user_origin_bp100 = user_origin_bps_pp[99]

    diffbp1 = user_origin_bp1 - avgbp1
    diffbp2 = user_origin_bp2 - avgbp2
    diffbp3 = user_origin_bp3 - avgbp3
    diffbp4 = user_origin_bp4 - avgbp4
    diffbp5 = user_origin_bp5 - avgbp5
    diffbp100 = user_origin_bp100 - avgbp100

    total_diff = diffbp1 + diffbp2 + diffbp3 + diffbp4 + diffbp5

    return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pp, end_pp, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff

# 数据模块-avgtth
def calculate_avg_tth_bak(user_id, tth_range):
    # tth默认单位，w

    # 处理一下tth_range
    now_tth = db_user.find_one({'id': user_id})[
        'statistics']['total_hits']
    start_tth = now_tth - tth_range
    end_tth = now_tth + tth_range

    range_users = db_user.find(
        {'statistics.total_hits': {'$gt': start_tth, '$lt': end_tth}})

    user_now_pp = db_user.find_one({'id': user_id})[
        'statistics']['pp']

    bp1_pps_list = []
    bp2_pps_list = []
    bp3_pps_list = []
    bp4_pps_list = []
    bp5_pps_list = []
    bp100_pps_list = []
    total_pps_list = []

    for range_user in range_users:

        try:
            bp1_pps_list.append(range_user['bps_pp'][0])
            bp2_pps_list.append(range_user['bps_pp'][1])
            bp3_pps_list.append(range_user['bps_pp'][2])
            bp4_pps_list.append(range_user['bps_pp'][3])
            bp5_pps_list.append(range_user['bps_pp'][4])
            bp100_pps_list.append(range_user['bps_pp'][99])
            total_pps_list.append(range_user['statistics']['pp'])
        except:
            pass

    # 随便找个list计数
    users_amount = len(bp1_pps_list)

    avgbp1 = np.mean(bp1_pps_list)
    avgbp2 = np.mean(bp2_pps_list)
    avgbp3 = np.mean(bp3_pps_list)
    avgbp4 = np.mean(bp4_pps_list)
    avgbp5 = np.mean(bp5_pps_list)
    avgbp100 = np.mean(bp100_pps_list)
    avgtotalpp = np.mean(total_pps_list)

    user_origin_bps_pp = db_user.find_one({'id': user_id})['bps_pp']

    user_origin_bp1 = user_origin_bps_pp[0]
    user_origin_bp2 = user_origin_bps_pp[1]
    user_origin_bp3 = user_origin_bps_pp[2]
    user_origin_bp4 = user_origin_bps_pp[3]
    user_origin_bp5 = user_origin_bps_pp[4]
    user_origin_bp100 = user_origin_bps_pp[99]

    diffbp1 = user_origin_bp1 - avgbp1
    diffbp2 = user_origin_bp2 - avgbp2
    diffbp3 = user_origin_bp3 - avgbp3
    diffbp4 = user_origin_bp4 - avgbp4
    diffbp5 = user_origin_bp5 - avgbp5
    diffbp100 = user_origin_bp100 - avgbp100

    total_diff = diffbp1 + diffbp2 + diffbp3 + diffbp4 + diffbp5

    return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_tth, end_tth, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp


def calculate_avg_pt_bak(user_id, pt_range):
    # pt默认单位h

    # 处理一下tth_range
    now_pt = db_user.find_one({'id': user_id})[
        'statistics']['play_time']
    start_pt = now_pt - pt_range
    end_pt = now_pt + pt_range

    range_users = db_user.find(
        {'statistics.play_time': {'$gt': start_pt, '$lt': end_pt}})

    user_now_pp = db_user.find_one({'id': user_id})[
        'statistics']['pp']

    bp1_pps_list = []
    bp2_pps_list = []
    bp3_pps_list = []
    bp4_pps_list = []
    bp5_pps_list = []
    bp100_pps_list = []
    total_pps_list = []

    for range_user in range_users:

        try:
            bp1_pps_list.append(range_user['bps_pp'][0])
            bp2_pps_list.append(range_user['bps_pp'][1])
            bp3_pps_list.append(range_user['bps_pp'][2])
            bp4_pps_list.append(range_user['bps_pp'][3])
            bp5_pps_list.append(range_user['bps_pp'][4])
            bp100_pps_list.append(range_user['bps_pp'][99])
            total_pps_list.append(range_user['statistics']['pp'])
        except:
            pass

    # 随便找个list计数
    users_amount = len(bp1_pps_list)

    avgbp1 = np.mean(bp1_pps_list)
    avgbp2 = np.mean(bp2_pps_list)
    avgbp3 = np.mean(bp3_pps_list)
    avgbp4 = np.mean(bp4_pps_list)
    avgbp5 = np.mean(bp5_pps_list)
    avgbp100 = np.mean(bp100_pps_list)
    avgtotalpp = np.mean(total_pps_list)

    user_origin_bps_pp = db_user.find_one({'id': user_id})['bps_pp']

    user_origin_bp1 = user_origin_bps_pp[0]
    user_origin_bp2 = user_origin_bps_pp[1]
    user_origin_bp3 = user_origin_bps_pp[2]
    user_origin_bp4 = user_origin_bps_pp[3]
    user_origin_bp5 = user_origin_bps_pp[4]
    user_origin_bp100 = user_origin_bps_pp[99]

    diffbp1 = user_origin_bp1 - avgbp1
    diffbp2 = user_origin_bp2 - avgbp2
    diffbp3 = user_origin_bp3 - avgbp3
    diffbp4 = user_origin_bp4 - avgbp4
    diffbp5 = user_origin_bp5 - avgbp5
    diffbp100 = user_origin_bp100 - avgbp100

    total_diff = diffbp1 + diffbp2 + diffbp3 + diffbp4 + diffbp5

    return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pt, end_pt, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp
