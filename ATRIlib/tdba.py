import numpy as np
from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.pp import WEIGHT_LIST
from ATRIlib.DRAW.draw_tdba import draw_tdba
from ATRIlib.DB.pipeline_tdba import get_tdba_sim_list_from_db
import datetime


# 计算tdba
def calculate_tdba(user_id):
    
    osuname = db_user.find_one({'id': user_id})['username']

    per_time = []  # 每个时间段0-23
    sum_pp_per_hour = []  # 每个时间段的累计pp

    pp_list = db_bp.find_one({'id': user_id})['bps_pp']
    list1 = np.array(pp_list)
    list2 = np.array(WEIGHT_LIST)
    weighted_pplist = list1 * list2
    time_list = db_bp.find_one({'id': user_id})['bps_createdate']

    for i in range(24):
        per_time.append(i)
        sum_pp_per_hour.append(0)

    for i in range(len(weighted_pplist)):
        formated_time = datetime.datetime.strptime(
            time_list[i], "%Y-%m-%dT%H:%M:%SZ")
        formated_time = formated_time + datetime.timedelta(hours=8)
        hours = formated_time.hour
        sum_pp_per_hour[hours] += weighted_pplist[i]

    # 散点图
    x_list = []
    y_list = []

    # 获取坐标
    for i in range(len(list1)):
        formated_time = datetime.datetime.strptime(
            time_list[i], "%Y-%m-%dT%H:%M:%SZ")
        formated_time = formated_time + datetime.timedelta(hours=8)
        hours = formated_time.hour
        x_list.append(hours)
        y_list.append(list1[i])

    data = draw_tdba(sum_pp_per_hour, per_time,
                            x_list, y_list, osuname)

    return data


# 计算tdba_vs
# def calculate_tdbavs(user_id, vs_id):
#
#     osuname = db_user.find_one({'id': user_id})['username']
#     vsname = db_user.find_one({'id': vs_id})['username']
#
#     per_time = []  # 每个时间段0-23
#     user1_sum_pp_per_hour = []  # 每个时间段的累计pp
#     user2_sum_pp_per_hour = []
#
#     user1_pp_list = db_user.find_one({'id': user_id})['bps_pp']
#     user2_pp_list = db_user.find_one({'id': vs_id})['bps_pp']
#     user1_rawpp_list = np.array(user1_pp_list)
#     weight_list = np.array(WEIGHT_LIST)
#     user1_weighted_pplist = user1_rawpp_list * weight_list
#     user2_rawpp_list = np.array(user2_pp_list)
#     user2_weighted_pplist = user2_rawpp_list * weight_list
#     user1_time_list = db_user.find_one({'id': user_id})[
#         'bps_createdat']
#     user2_time_list = db_user.find_one({'id': vs_id})['bps_createdat']
#
#     for i in range(24):
#         per_time.append(i)
#         user1_sum_pp_per_hour.append(0)
#         user2_sum_pp_per_hour.append(0)
#
#     for i in range(len(user1_weighted_pplist)):
#         formated_time = datetime.datetime.strptime(
#             user1_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
#         formated_time = formated_time + datetime.timedelta(hours=8)
#         hours = formated_time.hour
#         user1_sum_pp_per_hour[hours] += user1_weighted_pplist[i]
#
#     for i in range(len(user2_weighted_pplist)):
#         formated_time = datetime.datetime.strptime(
#             user2_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
#         formated_time = formated_time + datetime.timedelta(hours=8)
#         hours = formated_time.hour
#         user2_sum_pp_per_hour[hours] += user2_weighted_pplist[i]
#
#     # 散点图
#     user1_x_list = []
#     user1_y_list = []
#     user2_x_list = []
#     user2_y_list = []
#
#     # 获取坐标
#     for i in range(len(user1_rawpp_list)):
#         formated_time = datetime.datetime.strptime(
#             user1_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
#         formated_time = formated_time + datetime.timedelta(hours=8)
#         hours = formated_time.hour
#         user1_x_list.append(hours)
#         user1_y_list.append(user1_rawpp_list[i])
#
#     # 获取坐标
#     for i in range(len(user2_rawpp_list)):
#         formated_time = datetime.datetime.strptime(
#             user2_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
#         formated_time = formated_time + datetime.timedelta(hours=8)
#         hours = formated_time.hour
#         user2_x_list.append(hours)
#         user2_y_list.append(user2_rawpp_list[i])
#
#     data = draw_tdba_vs(user1_sum_pp_per_hour, user2_sum_pp_per_hour, per_time,
#                             user1_x_list, user1_y_list, user2_x_list, user2_y_list, osuname, vsname)
#
#     return data

def calculate_tdba_sim(user_id):

    raw = get_tdba_sim_list_from_db(user_id)

    return raw