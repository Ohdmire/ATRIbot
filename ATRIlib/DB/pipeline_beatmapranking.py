from .Mongodb import db_bind,db_group
from ATRIlib.TOOLS.osu_mod_multiplier import mod_multiplier


def _mods_to_acronyms(mods):
    if not mods:
        return []

    acronyms = []
    for mod in mods:
        if isinstance(mod, str):
            acronyms.append(mod)
        elif isinstance(mod, dict):
            acronym = mod.get("acronym")
            if acronym:
                acronyms.append(acronym)
    return acronyms


def _display_score(score):
    base_score = score.get("total_score_without_mods", score.get("total_score", 0))
    try:
        return int(round(base_score * mod_multiplier(_mods_to_acronyms(score.get("mods", [])))))
    except Exception:
        return int(base_score)


def _sort_by_display_score(records):
    result = []

    for record in records:
        scores = record.get("top_score", [])
        if not scores:
            continue

        for score in scores:
            score["display_score"] = _display_score(score)

        record["top_score"] = max(scores, key=lambda score: score["display_score"])
        result.append(record)

    result.sort(key=lambda record: record["top_score"].get("display_score", 0), reverse=True)
    return result

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

def get_beatmapranking_list_from_unrankscore_db(base_user_id, beatmap_id, group_id, modslist):
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
                "from": "unrankscore",
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
                            ),
                "as": "top_score"
            }
        },
        # 5. 投影出需要的字段
        {
            "$project": {
                "id": 1,
                "user_info.id": 1,
                "user_info.username": 1,
                "user_info.avatar_url": 1,
                "top_score": 1
            }
        }
    ]

    result = _sort_by_display_score(list(db_bind.aggregate(pipeline)))

    return result

def get_beatmapranking_list_from_unrankscore_db_old(base_user_id, beatmap_id, group_id, modslist):

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
                "from": "unrankscore",
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
                "user_info.id": 1,
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
                        ),
                "as": "top_score"
            }
        },
        # 5. 投影出需要的字段
        {
            "$project": {
                "id": 1,
                "user_info.id": 1,
                "user_info.username": 1,
                "user_info.avatar_url": 1,
                "top_score": 1
            }
        }
    ]

    result = _sort_by_display_score(list(db_bind.aggregate(pipeline)))

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
                "user_info.id": 1,
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
