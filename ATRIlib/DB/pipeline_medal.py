from ATRIlib.DB.Mongodb import db_medal,db_user

def get_medal_list_from_db(medalid):

    pipeline = [

        {
            "$match": {
                "medalid": {"$eq": medalid}
            }
        },

        {
            "$lookup": {
                "from": "solution",
                "localField": "medalid",
                "foreignField": "medalid",
                "as": "solution_data"
            }  # 合并medal_solution表
        },

        {
            "$unwind": "$solution_data"  # 解构表
        },

        {
            "$lookup": {
                "from": "rarity",
                "localField": "medalid",
                "foreignField": "id",
                "as": "rarity_data"
            }  # 合并medal_solution表
        },

        {
            "$unwind": "$rarity_data"  # 解构表
        },
    ]

    result = list(db_medal.aggregate(pipeline))

    return result

def get_user_medal_list_from_db(user_id):

    pipeline = [

        {
            "$match": {
                "id": user_id
            }
        },
        {
            "$unwind": "$user_achievements"  # 拆分数组为多个文档
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": {"$toDate": "$user_achievements.achieved_at"}},
                    "quarter": {"$ceil": {"$divide": [{"$month": {"$toDate": "$user_achievements.achieved_at"}}, 3]}}
                },
                "achievement_ids": {"$addToSet": "$user_achievements.achievement_id"},
                "count": {"$sum": 1}  # 你可以根据需要修改这个字段
            }
        },

        {
            "$project": {
                "_id": 0,
                "year": "$_id.year",
                "quarter": "$_id.quarter",
                "count": 1,
                "achievement_ids": 1
            }
        },

        {
            "$sort": {
                "year": -1,  # 按 year 降序排序
                "quarter": -1  # 按 quarter 降序排序
            }
        }

    ]

    result = list(db_user.aggregate(pipeline))

    return result

def get_user_special_medal_list_from_db(user_id):
    special_medal_list = [
        55,56,57,58,59,60,61,62,242,244,  # pass系列
        63,64,65,66,67,68,69,70,243,245  # FC系列
    ]

    pipeline = [
        {
            "$match": {
                "id": user_id
            }
        },
        {
            "$unwind": "$user_achievements"
        },
        {
            "$match": {
                "user_achievements.achievement_id": {"$in": special_medal_list}
            }
        },
        {
            "$project": {
                "_id": 0,
                "achievement_id": "$user_achievements.achievement_id",
                "achieved_at": "$user_achievements.achieved_at"
            }
        },
        {
            "$sort": {
                "achieved_at": 1 # 按获得时间升序排序
            }
        }
    ]

    result = list(db_user.aggregate(pipeline))

    print(result)
    
    return result
