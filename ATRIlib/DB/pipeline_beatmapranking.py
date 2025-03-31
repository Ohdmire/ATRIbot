from .Mongodb import db_bind,db_group

def get_beatmapranking_up_list_from_db(group_id):

    group_member_list = db_group.find_one({'id':group_id})['qq_id_list']

    # 聚合查询
    pipeline = [

        {
            "$match": {
                "id": {"$in": group_member_list}
            }
        },

    ]

    result = list(db_bind.aggregate(pipeline))

    return result

def get_beatmapranking_list_from_db(base_user_id, beatmap_id, group_id, modslist):
    group_member_list = db_group.find_one({'id': group_id})['qq_id_list']

    # 聚合查询
    pipeline = [
        # 1. 过滤出group中的成员
        {
            "$match": {
                "id": {"$in": group_member_list}
            }
        },
        # 2. 合并用户表，以获取更多的用户信息
        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_info"
            }
        },
        # 3. 展开user_info字段
        {
            "$unwind": "$user_info"
        },
        # 4. 从score表中获取每个玩家在特定beatmap上的最高分
        {
            "$lookup": {
                "from": "score",
                "let": {"user_id": "$user_id", "beatmap_id": beatmap_id},
                "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", "$$user_id"]},
                                            {"$eq": ["$beatmap_id", "$$beatmap_id"]},
                                        ]
                                    }
                                }
                            },
                        ] + (
                            [
                                # 如果modslist不为None，则添加以下$match条件
                                {
                                    "$match": {
                                        "$expr": {
                                            "$setEquals": ["$mods", modslist]
                                        }
                                    }
                                }
                            ] if modslist is not None else []
                        ) + [
                            {"$sort": {"total_score": 1}},
                            {"$limit": 1}
                        ],
                "as": "top_score"
            }
        },
        # 5. 展开top_score字段
        {
            "$unwind": "$top_score"
        },
        # 6. 投影出需要的字段
        {
            "$project": {
                "id": 1,
                "user_info.username": 1,
                "user_info.avatar_url": 1,
                "top_score": 1
            }
        },
        # 7. 按照 top_score 中的 score 字段排序
        {
            "$sort": {
                "top_score.total_score": 1  # -1 表示降序排序
            }
        }
    ]

    result = list(db_bind.aggregate(pipeline))

    return result

def get_beatmapranking_list_from_db_old(base_user_id, beatmap_id, group_id, modslist):

    group_member_list = db_group.find_one({'id': group_id})['qq_id_list']

    # 聚合查询
    pipeline = [
        # 1. 过滤出group中的成员
        {
            "$match": {
                "id": {"$in": group_member_list}
            }
        },
        # 2. 合并用户表，以获取更多的用户信息
        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_info"
            }
        },
        # 3. 展开user_info字段
        {
            "$unwind": "$user_info"
        },
        # 4. 从score表中获取每个玩家在特定beatmap上的最高分
        {
            "$lookup": {
                "from": "score",
                "let": {"user_id": "$user_id", "beatmap_id": beatmap_id},
                "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$and": [
                                                {"$eq": ["$user_id", "$$user_id"]},
                                                {"$eq": ["$beatmap_id", "$$beatmap_id"]},
                                            ]
                                        }
                                    }
                                },
                            ] + (
                                [
                                    # 如果modslist不为None，则添加以下$match条件
                                    {
                                        "$match": {
                                            "$expr": {
                                                "$setEquals": ["$mods", modslist]
                                            }
                                        }
                                    }
                                ] if modslist is not None else []
                            ) + [
                                {"$sort": {"legacy_total_score": -1}},
                                {"$limit": 1}
                            ],
                "as": "top_score"
            }
        },
        # 5. 展开top_score字段
        {
            "$unwind": "$top_score"
        },
        # 6. 投影出需要的字段
        {
            "$project": {
                "id": 1,
                "user_info.username": 1,
                "user_info.avatar_url": 1,
                "top_score": 1
            }
        },
        # 7. 按照 top_score 中的 score 字段排序
        {
            "$sort": {
                "top_score.legacy_total_score": -1  # -1 表示降序排序
            }
        }
    ]

    result = list(db_bind.aggregate(pipeline))

    return result