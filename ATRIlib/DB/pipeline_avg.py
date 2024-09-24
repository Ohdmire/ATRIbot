from .Mongodb import db_user,db_bp
import datetime

def get_avgpp_list_from_db(base_user_id,pp_range):
    
    # 处理pp范围
    now_pp = db_user.find_one({"id": base_user_id})['statistics']['pp']
    start_pp = now_pp - pp_range
    end_pp = now_pp + pp_range


    pipeline = [
        {
            "$match": {
                "statistics.pp": {"$gte": start_pp, "$lte": end_pp}  # pp值在范围内
            }
        },

        {
            "$lookup": {
                "from": "bp",
                "localField": "id",
                "foreignField": "id",
                "as": "bp_data"
            }  # 合并bp表
        },

        {
            "$unwind": "$bp_data"  # 解构表
        },
        
        {
            "$project": {
                "statistics.pp":1,
                "firstElement": {"$arrayElemAt": ["$bp_data.bps_pp", 0]},
                "secondElement": {"$arrayElemAt": ["$bp_data.bps_pp", 1]},
                "thirdElement": {"$arrayElemAt": ["$bp_data.bps_pp", 2]},
                "fourthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 3]},
                "fifthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 4]},
                "lastElement": {"$arrayElemAt": ["$bp_data.bps_pp", 99]}
            }
        },
        {
            "$group": {
                "_id": None,
                "avgpp":{"$avg": "$statistics.pp"},
                "avgbp1": {"$avg": "$firstElement"},
                "avgbp2": {"$avg": "$secondElement"},
                "avgbp3": {"$avg": "$thirdElement"},
                "avgbp4": {"$avg": "$fourthElement"},
                "avgbp5": {"$avg": "$fifthElement"},
                "avgbp100": {"$avg": "$lastElement"},
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(db_user.aggregate(pipeline))

    endtime = datetime.datetime.now()

    return result

def get_avgpt_list_from_db(base_user_id, pt_range):
    # 处理pt范围
    now_play_time = db_user.find_one({"id": base_user_id})['statistics']['play_time']
    start_play_time = now_play_time - pt_range
    end_play_time = now_play_time + pt_range

    pipeline = [
        {
            "$match": {
                "statistics.play_time": {"$gte": start_play_time, "$lte": end_play_time}  # play_time值在范围内
            }
        },

        {
            "$lookup": {
                "from": "bp",
                "localField": "id",
                "foreignField": "id",
                "as": "bp_data"
            }  # 合并bp表
        },

        {
            "$unwind": "$bp_data"  # 解构表
        },

        {
            "$project": {
                "statistics.pp": 1,
                "statistics.play_time": 1,
                "firstElement": {"$arrayElemAt": ["$bp_data.bps_pp", 0]},
                "secondElement": {"$arrayElemAt": ["$bp_data.bps_pp", 1]},
                "thirdElement": {"$arrayElemAt": ["$bp_data.bps_pp", 2]},
                "fourthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 3]},
                "fifthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 4]},
                "lastElement": {"$arrayElemAt": ["$bp_data.bps_pp", 99]}
            }
        },


        {
            "$group": {
                "_id": None,
                "avgpt": {"$avg": "$statistics.play_time"},
                "avgpp": {"$avg": "$statistics.pp"},
                "avgbp1": {"$avg": "$firstElement"},
                "avgbp2": {"$avg": "$secondElement"},
                "avgbp3": {"$avg": "$thirdElement"},
                "avgbp4": {"$avg": "$fourthElement"},
                "avgbp5": {"$avg": "$fifthElement"},
                "avgbp100": {"$avg": "$lastElement"},
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(db_user.aggregate(pipeline))

    return result

def get_avgtth_list_from_db(base_user_id, tth_range):
    # 处理tth范围
    now_tth = db_user.find_one({"id": base_user_id})['statistics']['total_hits']
    start_tth = now_tth - tth_range
    end_tth = now_tth + tth_range

    pipeline = [
        {
            "$match": {
                "statistics.total_hits": {"$gte": start_tth, "$lte": end_tth}  # tth值在范围内
            }
        },

        {
            "$lookup": {
                "from": "bp",
                "localField": "id",
                "foreignField": "id",
                "as": "bp_data"
            }  # 合并bp表
        },

        {
            "$unwind": "$bp_data"  # 解构表
        },

        {
            "$project": {
                "statistics.pp": 1,
                "statistics.total_hits": 1,
                "firstElement": {"$arrayElemAt": ["$bp_data.bps_pp", 0]},
                "secondElement": {"$arrayElemAt": ["$bp_data.bps_pp", 1]},
                "thirdElement": {"$arrayElemAt": ["$bp_data.bps_pp", 2]},
                "fourthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 3]},
                "fifthElement": {"$arrayElemAt": ["$bp_data.bps_pp", 4]},
                "lastElement": {"$arrayElemAt": ["$bp_data.bps_pp", 99]}
            }
        },

        {
            "$group": {
                "_id": None,
                "avgtth": {"$avg": "$statistics.total_hits"},
                "avgpp": {"$avg": "$statistics.pp"},
                "avgbp1": {"$avg": "$firstElement"},
                "avgbp2": {"$avg": "$secondElement"},
                "avgbp3": {"$avg": "$thirdElement"},
                "avgbp4": {"$avg": "$fourthElement"},
                "avgbp5": {"$avg": "$fifthElement"},
                "avgbp100": {"$avg": "$lastElement"},
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(db_user.aggregate(pipeline))

    return result
