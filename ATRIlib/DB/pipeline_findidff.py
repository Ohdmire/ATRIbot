from ATRIlib.DB.Mongodb import db_bind, db_yesterday, db_user, db_score, db_group

def find_differences(group_id):

    group_member_list = db_group.find_one({'id':group_id})['qq_id_list']

    pipeline = [

        # 新增：筛选bind表中的id
        {"$match": {"id": {"$in": group_member_list}}},
        # 前面的步骤保持不变
        {"$lookup": {
            "from": "yesterday",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "yesterday_data"
        }},
        {"$unwind": "$yesterday_data"},
        # 过滤掉没有 yesterday_data 的用户
        {"$match": {"yesterday_data": {"$ne": []}}},    
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
        # 过滤掉没有 bp_data 的用户
        {"$match": {"bp_data": {"$ne": []}}},
        # 修改 project 阶段
        {"$project": {
            "user_id": 1,
            "username": 1,
            "differences": {
                "$filter": {
                    "input": {"$zip": {
                        "inputs": [
                            {"$ifNull": ["$bp_data.bps_beatmapid", []]},
                            {"$ifNull": ["$bp_data.bps_pp", []]}
                        ]
                    }},
                    "as": "today_item",
                    "cond": {
                        "$and": [
                            {"$ne": [{"$arrayElemAt": ["$$today_item", 0]}, 'null']},
                            {"$ne": [{"$arrayElemAt": ["$$today_item", 1]}, 'null']},
                            {"$not": {
                                "$in": [
                                    "$$today_item",
                                    {"$ifNull": [
                                        {"$zip": {
                                            "inputs": [
                                                {"$ifNull": ["$yesterday_data.bp_data.bps_beatmapid", []]},
                                                {"$ifNull": ["$yesterday_data.bp_data.bps_pp", []]}
                                            ]
                                        }},
                                        []
                                    ]}
                                ]
                            }}
                        ]
                    }
                }
            }
        }},
        {"$match": {"differences": {"$ne": []}}},
        
        # 新增：展开differences数组
        {"$unwind": "$differences"},
        
        # 新增：查找score表中的最高pp成绩
        {"$lookup": {
            "from": "score",
            "let": {"user_id": "$user_id", "beatmap_id": {"$arrayElemAt": ["$differences", 0]}},
            "pipeline": [
                {"$match": 
                    {"$expr": 
                        {"$and": [
                            {"$eq": ["$user_id", "$$user_id"]},
                            {"$eq": ["$beatmap_id", "$$beatmap_id"]}
                        ]}
                    }
                },
                {"$sort": {"pp": -1}},
                {"$limit": 1}
            ],
            "as": "best_score"
        }},
        {"$unwind": "$best_score"},
        
        # 修改：比较当前pp和最高pp，计算差值
        {"$project": {
            "user_id": 1,
            "username": 1,
            "beatmap_id": {"$arrayElemAt": ["$differences", 0]},
            "current_pp": {"$arrayElemAt": ["$differences", 1]},
            "best_pp": "$best_score.pp",
            "pp_difference": {"$subtract": [{"$arrayElemAt": ["$differences", 1]}, "$best_score.pp"]}
        }},
        
        # 新增：只保留当前pp低于最高pp的记录
        {"$match": {"pp_difference": {"$lt": 0}}},
        
        # 新增：按user_id分组并计算总pp差值
        {"$group": {
            "_id": "$user_id",
            "username": {"$first": "$username"},
            "total_pp_difference": {"$sum": "$pp_difference"},
            "details": {"$push": {
                "beatmap_id": "$beatmap_id",
                "current_pp": "$current_pp",
                "best_pp": "$best_pp",
                "pp_difference": "$pp_difference"
            }}
        }},
        
        # 修改：按总pp差值升序排序（负数最多的在前面）
        {"$sort": {"total_pp_difference": 1}}
    ]

    results = list(db_bind.aggregate(pipeline))
    return results

def find_differences_details(user_id):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "yesterday",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "yesterday_data"
        }},
        {"$unwind": "$yesterday_data"},
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
        {"$project": {
            "user_id": 1,
            "username": 1,
            "differences": {
                "$filter": {
                    "input": {"$zip": {
                        "inputs": [
                            "$bp_data.bps_beatmapid",
                            "$bp_data.bps_pp"
                        ]
                    }},
                    "as": "today_item",
                    "cond": {
                        "$not": {
                            "$in": [
                                "$$today_item",
                                {"$zip": {
                                    "inputs": [
                                        "$yesterday_data.bp_data.bps_beatmapid",
                                        "$yesterday_data.bp_data.bps_pp"
                                    ]
                                }}
                            ]
                        }
                    }
                }
            }
        }},
        {"$unwind": "$differences"},
        {"$lookup": {
            "from": "score",
            "let": {"user_id": "$user_id", "beatmap_id": {"$arrayElemAt": ["$differences", 0]}},
            "pipeline": [
                {"$match": 
                    {"$expr": 
                        {"$and": [
                            {"$eq": ["$user_id", "$$user_id"]},
                            {"$eq": ["$beatmap_id", "$$beatmap_id"]}
                        ]}
                    }
                },
                {"$sort": {"pp": -1}},
                {"$limit": 1}
            ],
            "as": "best_score"
        }},
        {"$unwind": "$best_score"},
        {"$project": {
            "user_id": 1,
            "username": 1,
            "beatmap_id": {"$arrayElemAt": ["$differences", 0]},
            "current_pp": {"$arrayElemAt": ["$differences", 1]},
            "best_pp": "$best_score.pp",
            "pp_difference": {"$subtract": [{"$arrayElemAt": ["$differences", 1]}, "$best_score.pp"]}
        }},
        {"$match": {"pp_difference": {"$lt": 0}}},
        {"$sort": {"pp_difference": 1}}
    ]

    results = list(db_bind.aggregate(pipeline))
    return results
