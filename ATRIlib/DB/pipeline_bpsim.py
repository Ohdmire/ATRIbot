from .Mongodb import db_user,db_bind,db_bp
from ..DRAW.Draw import result_result_path


def get_sim_list_from_db(base_user_id,pp_range):

    # 处理pp范围
    now_pp = db_user.find_one({"id": base_user_id})['statistics']['pp']
    start_pp = now_pp - pp_range
    end_pp = now_pp + pp_range

    # 获取基准玩家的beatmapid数组
    base_user_bp = db_bp.find_one({"id": base_user_id})
    base_beatmapids = base_user_bp['bps_beatmapid']

    # 聚合查询
    # pipeline = [
    #     {
    #         "$match": {
    #
    #             "statistics.pp": {"$gte": start_pp, "$lte": end_pp}  # pp值在范围内
    #         }
    #     },
    #     {
    #         "$lookup": {
    #             "from": "bind",
    #             "localField": "id",
    #             "foreignField": "user_id",
    #             "as": "bind_data"
    #         } # 合并bind表
    #     },
    #     {
    #         "$match": {
    #             "bind_data": {"$ne": []}  # 过滤掉没有 bind_data 的用户（未绑定的用户）
    #         }
    #     },
    #     {
    #         "$project": {
    #             "id": 1,
    #             "username": 1,
    #             "sim_count": {
    #                 "$size": {
    #                     "$cond": {
    #                         "if": {"$isArray": {"$setIntersection": ["$bps_beatmapid", base_beatmapids]}},
    #                         "then": {"$setIntersection": ["$bps_beatmapid", base_beatmapids]},
    #                         "else": []
    #                     }
    #                 }
    #             }
    #         }
    #     },
    #     {
    #         "$sort": {
    #             "sim_count": -1  # 按重合数量降序排序
    #         }
    #     },
    #     {
    #         "$limit": 11  # 获取重合最多的玩家top10
    #     }
    # ]

    pipeline = [
        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_data"
            }  # 合并bind表
        },
        {
            "$match": {
                "user_data": {"$ne": []},  # 过滤掉没有 user信息 的用户（获取信息失败的用户）
                "user_data.statistics.pp": {"$gte": start_pp, "$lte": end_pp}  # pp值在范围内
            }
        },

        {
            "$unwind": "$user_data" #解构表
        },

        {
            "$lookup": {
                "from": "bp",
                "localField": "user_id",
                "foreignField": "id",
                "as": "bp_data"
            }  # 合并bp表
        },

        {
            "$unwind": "$bp_data"  # 解构表
        },

        {

            "$project": {
            "user_data.id": 1,
            "user_data.username": 1,
            "sim_count": {
                "$size": {
                        "$setIntersection": ["$bp_data.bps_beatmapid", base_beatmapids]
                    }
                }
            }
        },

    {
        "$sort": {
            "sim_count": -1  # 按重合数量降序排序
        }
    },
    {
        "$limit": 11  # 获取重合最多的玩家top10
    }

    ]

    # result = list(db_user.aggregate(pipeline))

    result = list(db_bind.aggregate(pipeline))

    return result