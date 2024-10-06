from ATRIlib.DB.Mongodb import db_bind, db_yesterday, db_user, db_score, db_group

def find_differences(group_id):

    group_member_list = db_group.find_one({'id':group_id})['qq_id_list']


    pipeline = [

        # 新增：筛选bind表中的id
        {"$match": {"user_id": {"$in": group_member_list}}},
        # 前面的步骤保持不变
        {"$lookup": {
            "from": "yesterday",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "yesterday_data"
        }},
        {"$unwind": "$yesterday_data"},
        # 确保 username 被添加到文档中
        {"$addFields": {
            "username": "$yesterday_data.user_data.username"
        }},
        
        {"$lookup": {
            "from": "bp",
            "localField": "user_id",
            "foreignField": "id",
            "as": "bp_data"
        }},
        {"$unwind": "$bp_data"},
        # 确保在 project 阶段保留 username
        {"$project": {
            "user_id": 1,
            "username": 1,  # 保留 username
            "differences": {
                "$filter": {
                    "input": {"$zip": {
                        "inputs": [
                            "$yesterday_data.bp_data.bps_beatmapid",
                            "$yesterday_data.bp_data.bps_pp"
                        ]
                    }},
                    "as": "yesterday_item",
                    "cond": {
                        "$not": {
                            "$in": [
                                "$$yesterday_item",
                                {"$zip": {
                                    "inputs": [
                                        "$bp_data.bps_beatmapid",
                                        "$bp_data.bps_pp"
                                    ]
                                }}
                            ]
                        }
                    }
                }
            }
        }},
        {"$match": {"differences": {"$ne": []}}},
        # 新增步骤：查询score数据库并计算差值
        {"$unwind": "$differences"},
        {"$lookup": {
            "from": "score",
            "let": {
                "user_id": "$user_id",
                "beatmap_id": {"$arrayElemAt": ["$differences", 0]}
            },
            "pipeline": [
                {"$match": {
                    "$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$user_id"]},
                            {"$eq": ["$beatmap_id", "$$beatmap_id"]}
                        ]
                    }
                }},
                {"$sort": {"pp": -1}},
                {"$limit": 1}
            ],
            "as": "score_data"
        }},
        {"$unwind": {"path": "$score_data", "preserveNullAndEmptyArrays": True}},
        # 在这里也保留 username
        {"$project": {
            "user_id": 1,
            "username": 1,  # 保留 username
            "beatmap_id": {"$arrayElemAt": ["$differences", 0]},
            "yesterday_pp": {"$arrayElemAt": ["$differences", 1]},
            "score_pp": "$score_data.pp",
            "pp_difference": {
                "$cond": {
                    "if": {"$gt": ["$score_data.pp", {"$arrayElemAt": ["$differences", 1]}]},
                    "then": {"$subtract": [{"$arrayElemAt": ["$differences", 1]}, "$score_data.pp"]},
                    "else": None
                }
            }
        }},
        {"$match": {"pp_difference": {"$ne": None}}},
        {"$group": {
            "_id": "$user_id",
            "user_id": {"$first": "$user_id"},
            "username": {"$first": "$username"},  # 保留 username
            "differences": {
                "$push": {
                    "beatmap_id": "$beatmap_id",
                    "yesterday_pp": "$yesterday_pp",
                    "score_pp": "$score_pp",
                    "pp_difference": "$pp_difference"
                }
            },
            "total_pp_difference": {"$sum": "$pp_difference"}  # 计算总的 PP 差值
        }},
        # 重新组织输出字段
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "username": 1,  # 包含 username 在输出中
            "differences": 1,
            "total_pp_difference": 1
        }},
        # 按总 PP 差值排序
        {"$sort": {"total_pp_difference": 1}}  # 1 表示升序，最大负数（总下降最多）会在最前面
    ]

    results = list(db_bind.aggregate(pipeline))
    return results