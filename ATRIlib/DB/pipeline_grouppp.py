from .Mongodb import db_bind, db_group


def get_group_pp_list_from_db(group_id):

    group_member_list = db_group.find_one({'id': group_id})['qq_id_list']

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
                # 过滤掉没有 user信息 的用户，以及还没打过分(pp为0)的用户
                "user_data.statistics.pp": {"$gt": 0}
            }
        },

        {
            "$project": {
                "_id": 0,
                "user_id": "$user_data.id",
                "username": "$user_data.username",
                "pp": "$user_data.statistics.pp",
            }
        },

        {
            "$sort": {
                "pp": -1,
                "user_id": 1  # pp相同时按id排序，保证名次稳定
            }
        }
    ]

    result = list(db_bind.aggregate(pipeline))

    return result
