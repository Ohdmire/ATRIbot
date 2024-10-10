from ATRIlib.DB.Mongodb import db_bp, db_user, db_group, db_yesterday, db_bind
import datetime

def pipeline_daily_bp_data(group_id):

    group_info = db_group.find_one({"id": group_id})
    group_members_list = group_info['qq_id_list']

    now = datetime.datetime.now()
    now_utc = now - datetime.timedelta(hours=8)
    
    today_4am_utc = now_utc.replace(hour=4, minute=0, second=0, microsecond=0)
    
    if now_utc < today_4am_utc:
        start_time = today_4am_utc - datetime.timedelta(days=1)
        end_time = today_4am_utc
    else:
        start_time = today_4am_utc
        end_time = start_time + datetime.timedelta(days=1)

    pipeline = [
        {
            "$lookup": {
                "from": "bind",
                "localField": "id",
                "foreignField": "user_id",
                "as": "bind_info"
            }
        },
        {
            "$match": {
                "bind_info": {"$ne": []}  # 确保只选择已绑定的用户
            }
        },
        {
            "$match": {
                "bind_info.id": {"$in": group_members_list}
            }
        },
        {
            "$project": {
                "zipped_data": {
                    "$zip": {
                        "inputs": ["$bps_createdate", "$bps_pp"]
                    }
                },
                "id": 1
            }
        },
        {
            "$unwind": "$zipped_data"
        },
        {
            "$project": {
                "bps_createdate": {
                    "$dateFromString": {
                        "dateString": {"$arrayElemAt": ["$zipped_data", 0]},
                        "format": "%Y-%m-%dT%H:%M:%SZ"
                    }
                },
                "bps_pp": {"$arrayElemAt": ["$zipped_data", 1]},
                "id": 1
            }
        },
        {
            "$match": {
                "bps_createdate": {
                    "$gte": start_time,
                    "$lt": end_time
                }
            }
        },
        {
            "$group": {
                "_id": "$id",
                "pp_array": {"$push": "$bps_pp"}
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "_id",
                "foreignField": "id",
                "as": "user_info"
            }
        },
        {
            "$unwind": "$user_info"
        },
        {
            "$project": {
                "id": "$_id",
                "username": "$user_info.username",
                "pp_array": 1,
                "_id": 0
            }
        }
    ]

    results = list(db_bp.aggregate(pipeline))

    return results

def pipeline_daily_other_data(group_id):

    group_info = db_group.find_one({"id": group_id})
    group_members_list = group_info['qq_id_list']

    pipeline = [
        {
            "$match": {
                "id": {"$in": group_members_list}
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_data"
            }
        },
        {
            "$unwind": "$user_data"
        },
        {
            "$lookup": {
                "from": "yesterday",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "yesterday_data"
            }
        },
        {
            "$unwind": {
                "path": "$yesterday_data",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "id": "$user_data.id",
                "username": "$user_data.username",
                "play_count": "$user_data.statistics.play_count",
                "yesterday_play_count": "$yesterday_data.user_data.statistics.play_count",
                "play_count_change": {
                    "$subtract": ["$user_data.statistics.play_count", {"$ifNull": ["$yesterday_data.user_data.statistics.play_count", "$user_data.statistics.play_count"]}]
                },
                "play_time_hours": {
                    "$divide": ["$user_data.statistics.play_time", 3600]
                },
                "yesterday_play_time_hours": {
                    "$divide": [
                        {"$ifNull": ["$yesterday_data.user_data.statistics.play_time", 0]},
                        3600
                    ]
                },
                "play_time_change_hours": {
                    "$divide": [
                        {
                            "$subtract": [
                                "$user_data.statistics.play_time",
                                {"$ifNull": ["$yesterday_data.user_data.statistics.play_time", "$user_data.statistics.play_time"]}
                            ]
                        },
                        3600
                    ]
                },
                "total_hits_w": {
                    "$divide": ["$user_data.statistics.total_hits", 10000]
                },
                "yesterday_total_hits_w": {
                    "$divide": [
                        {"$ifNull": ["$yesterday_data.user_data.statistics.total_hits", 0]},
                        10000
                    ]
                },
                "total_hits_change_w": {
                    "$divide": [
                        {
                            "$subtract": [
                                "$user_data.statistics.total_hits",
                                {"$ifNull": ["$yesterday_data.user_data.statistics.total_hits", "$user_data.statistics.total_hits"]}
                            ]
                        },
                        10000
                    ]
                },
                "global_rank": "$user_data.statistics.global_rank",
                "yesterday_global_rank": "$yesterday_data.user_data.statistics.global_rank",
                "global_rank_change": {
                    "$subtract": [
                        {"$ifNull": ["$yesterday_data.user_data.statistics.global_rank", "$user_data.statistics.global_rank"]},
                        "$user_data.statistics.global_rank"
                    ]
                },
                "pp": "$user_data.statistics.pp",
                "yesterday_pp": "$yesterday_data.user_data.statistics.pp",
                "pp_change": {
                    "$subtract": [
                        "$user_data.statistics.pp",
                        {"$ifNull": ["$yesterday_data.user_data.statistics.pp", "$user_data.statistics.pp"]}
                    ]
                }
            }
        },
        {
            "$match": {
                "$or": [
                    {"play_count_change": {"$ne": 0}},
                    {"play_time_change_hours": {"$ne": 0}},
                    {"total_hits_change_w": {"$ne": 0}},
                    {"global_rank_change": {"$ne": 0}},
                    {"pp_change": {"$ne": 0}}
                ]
            }
        },
    ]

    results = list(db_bind.aggregate(pipeline))

    return results