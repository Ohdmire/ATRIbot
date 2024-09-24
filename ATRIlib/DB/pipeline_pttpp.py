from .Mongodb import db_user, db_bp


def get_avgpp_pttpp_from_db(base_user_id, pp_range):
    # 处理pp范围
    now_pp = db_user.find_one({"id": base_user_id})['statistics']['pp']
    start_pp = now_pp - 500
    end_pp = now_pp + 500

    pipeline = [
        {
            "$match": {
                "statistics.pp": {"$gte": start_pp, "$lte": end_pp}  # pp值在范围内
            }
        },

        {
            "$lookup": {
                "from": "bp",
                "localField": "id",
                "foreignField": "id",
                "as": "bp_data"
            }  # 合并bp表
        },

        {
            "$unwind": "$bp_data"  # 解构表
        },

        {
            "$project": {
                "statistics.pp": 1,
                "bp2pp": {"$arrayElemAt": ["$bp_data.bps_pp", 1]},
            }
        }
    ]

    result = list(db_user.aggregate(pipeline))

    return result
