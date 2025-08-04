from .Mongodb import db_user


def get_matched_pp_list(base_user_id, pp_range, star_min=5, star_max=7):
    """
    获取匹配PP范围内的用户及其BP数据，排除包含黑名单mod的记录

    参数:
        base_user_id: 基础用户ID
        pp_range: PP范围浮动值
        star_min: 最小星数(默认4)
        star_max: 最大星数(默认4)
        mod_blacklist: 需要排除的mod列表(如['DT', 'HD']), 默认None表示不排除
    """
    # 获取当前用户的pp值并计算范围
    now_pp = db_user.find_one({"id": base_user_id})['statistics']['pp']
    start_pp = now_pp - pp_range
    end_pp = now_pp + pp_range

    # mod_blacklist = ["DT","EZ","HR","FL"]
    mod_blacklist = []

    pipeline = [
        # 1. 匹配 PP 范围内的用户
        {
            "$match": {
                "statistics.pp": {"$gte": start_pp, "$lte": end_pp}
            }
        },
        # 2. 关联 BP 数据
        {
            "$lookup": {
                "from": "bp",
                "localField": "id",
                "foreignField": "id",
                "as": "bp_data"
            }
        },
        # 3. 解构 BP 数据（只处理有数据的用户）
        {
            "$unwind": "$bp_data"
        },
        # 4. 确保 bps_star、bps_pp和bps_mods是数组且长度相同
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$isArray": "$bp_data.bps_star"},
                        {"$isArray": "$bp_data.bps_pp"},
                        {"$isArray": "$bp_data.bps_mods"},
                        {"$eq": [
                            {"$size": "$bp_data.bps_star"},
                            {"$size": "$bp_data.bps_pp"}
                        ]},
                        {"$eq": [
                            {"$size": "$bp_data.bps_star"},
                            {"$size": "$bp_data.bps_mods"}
                        ]}
                    ]
                }
            }
        },
        # 5. 使用 $zip 合并 star、pp和mods
        {
            "$project": {
                "user_id": "$id",
                "matched_data": {
                    "$zip": {
                        "inputs": ["$bp_data.bps_star", "$bp_data.bps_pp", "$bp_data.bps_mods"],
                        "useLongestLength": False
                    }
                }
            }
        },
        # 6. 解构并筛选符合星数范围且不包含黑名单mod的记录
        {
            "$unwind": "$matched_data"
        },
        {
            "$project": {
                "user_id": 1,
                "star": {"$arrayElemAt": ["$matched_data", 0]},
                "pp": {"$arrayElemAt": ["$matched_data", 1]},
                "mods": {"$arrayElemAt": ["$matched_data", 2]}
            }
        },
        {
            "$match": {
                "star": {"$gte": star_min, "$lte": star_max},
                # 只有当黑名单不为空时才应用mod过滤
                **(
                    {
                        "$expr": {
                            "$not": {
                                "$anyElementTrue": {
                                    "$map": {
                                        "input": "$mods",
                                        "as": "mod",
                                        "in": {
                                            "$in": ["$$mod.acronym", mod_blacklist]
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if mod_blacklist else {}
                )
            }
        }
    ]

    # 执行查询并返回结果
    result = list(db_user.aggregate(pipeline))

    return result