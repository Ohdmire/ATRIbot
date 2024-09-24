from .Mongodb import db_user, db_bp

def get_tdba_list_from_db(base_user_id):
    pass

def get_tdba_sim_list_from_db(base_user_id):
    pipeline = [
        # 过滤表
        {
            "$lookup": {
                "from": "bind",
                "localField": "id",
                "foreignField": "user_id",
                "as": "bind_data"
            }
        },
        {
            "$unwind": "$bind_data"
        },
        {
            "$match": {
                "bind_data": {"$ne": []},  # 过滤掉没有 bind 的用户
            }
        },

        # 1. 展开 bps_createdate 和 bps_pp 数组，提取小时信息
        {
            "$unwind": {
                "path": "$bps_createdate",
                "includeArrayIndex": "index_time"
            }
        },
        {
            "$unwind": {
                "path": "$bps_pp",
                "includeArrayIndex": "index_pp"
            }
        },
        # 2. 匹配两个数组的索引，以确保 bps_createdate 和 bps_pp 一一对应
        {
            "$match": {
                "$expr": {"$eq": ["$index_time", "$index_pp"]}
            }
        },
        # 3. 提取小时值
        {
            "$addFields": {
                "hour": {"$hour": {"$toDate": "$bps_createdate"}}
            }
        },
        # 4. 按小时分组，累加每个玩家每小时的 pp 值
        {
            "$group": {
                "_id": {"id": "$id", "hour": "$hour"},
                "totalPP": {"$sum": "$bps_pp"}
            }
        },
        # 5. 计算每个玩家每小时的权重
        {
            "$group": {
                "_id": "$_id.id",  # 分组按玩家 ID
                "hourlyData": {
                    "$push": {"hour": "$_id.hour", "totalPP": "$totalPP"}
                },
                "totalPPOverall": {"$sum": "$totalPP"}
            }
        },
        {
            "$project": {
                "id": "$_id",
                "_id": 0,
                "hourlyData": 1,
                "weights": {
                    "$map": {
                        "input": "$hourlyData",
                        "as": "hourData",
                        "in": {"hour": "$$hourData.hour",
                               "weight": {"$divide": ["$$hourData.totalPP", "$totalPPOverall"]}}
                    }
                }
            }
        },
        # 6. 计算玩家之间的余弦相似度
        {
            "$facet": {
                "targetPlayer": [
                    {"$match": {"id": base_user_id}},  # 使用 base_user_id 作为目标玩家 ID
                    {"$project": {"id": 1,"weights": 1}}
                ],
                "allOthers": [
                    {"$match": {"id": {"$ne": base_user_id}}},  # 排除目标玩家自己
                    {"$project": {"id": 1, "weights": 1}}
                ]
            }
        },
        {
            "$unwind": "$targetPlayer"
        },
        {
            "$unwind": "$allOthers"
        },
        # 7. 对每个其他玩家计算余弦相似度
        {
            "$project": {
                "id": "$allOthers.id",
                "weightsOther": "$allOthers.weights",
                "weightsTarget": "$targetPlayer.weights",
                "dotProduct": {
                    "$reduce": {
                        "input": {
                            "$zip": {"inputs": ["$allOthers.weights.weight", "$targetPlayer.weights.weight"]}
                        },
                        "initialValue": 0,
                        "in": {
                            "$add": [
                                "$$value",
                                {"$multiply": [
                                {"$arrayElemAt": ["$$this", 0]},
                                {"$arrayElemAt": ["$$this", 1]}
                            ]}
                            ]
                        }
                    }
                },
                "magnitudeOther": {
                    "$sqrt": {
                        "$reduce": {
                            "input": "$allOthers.weights.weight",
                            "initialValue": 0,
                            "in": {"$add": ["$$value", {"$multiply": ["$$this", "$$this"]}]}
                        }
                    }
                },
                "magnitudeTarget": {
                    "$sqrt": {
                        "$reduce": {
                            "input": "$targetPlayer.weights.weight",
                            "initialValue": 0,
                            "in": {"$add": ["$$value", {"$multiply": ["$$this", "$$this"]}]}
                        }
                    }
                }
            }
        },
        # 8. 计算余弦相似度
        {
            "$project": {
                "id": 1,
                "cosineSimilarity": {
                    "$divide": [
                        "$dotProduct",
                        {"$multiply": ["$magnitudeOther", "$magnitudeTarget"]}
                    ]
                }
            }
        },
        # 9. 按相似度排序，找出最相似的玩家
        {
            "$sort": {"cosineSimilarity": -1}
        },
        # 10. 绑定用户信息
        {
            "$lookup": {
                "from": "user",
                "localField": "id",
                "foreignField": "id",
                "as": "user_data"
            }  # 合并user表
        },
            {
                "$unwind": "$user_data"  # 解构表
            },

    ]


    result = list(db_bp.aggregate(pipeline))

    return result
