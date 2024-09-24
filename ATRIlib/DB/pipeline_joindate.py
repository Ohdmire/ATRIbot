from .Mongodb import db_user,db_bind,db_group

def get_joindate_group_list_from_db(base_user_id,group_id,pp_range):

    group_member_list = db_group.find_one({'id':group_id})['qq_id_list']

    # 处理一下pp_range
    now_pp = db_user.find_one({'id': base_user_id})['statistics']['pp']
    start_pp = now_pp - pp_range
    end_pp = now_pp + pp_range

    # 聚合查询
    pipeline = [

        {
            "$match": {
                "id": {"$in": group_member_list}
            }
        },

        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_data"
            }  # 合并bind表
        },

        {
            "$unwind": "$user_data"
        },

        {
            "$match": {
                "user_data": {"$ne": []},  # 过滤掉没有 user信息 的用户（获取信息失败的用户）
                "user_data.statistics.pp": {"$gte": start_pp, "$lte": end_pp}  # pp值在范围内
            }
        },
        {
            "$project": {
            "user_data.id": 1,
            "user_data.username": 1,
            "user_data.join_date": 1,
            }
        },
        {
            "$sort": {
                "user_data.join_date": 1  # 按重合数量降序排序
            }
        },
        {
            "$setWindowFields": {
                "sortBy": {"user_data.join_date": 1},
                "output": {
                    "joindate_rank": {"$rank": {}}
                }
            }
        },
    ]

    result = list(db_bind.aggregate(pipeline))

    return result