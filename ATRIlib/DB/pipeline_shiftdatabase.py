from ATRIlib.DB.Mongodb import db_bind, db_yesterday

def pipeline_shiftdatabase():
    pipeline = [
        # 从user获取数据
        {
            "$lookup": {
                "from": "user",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_data"
            }
        },
        {
            "$unwind": {
                "path": "$user_data",
                "preserveNullAndEmptyArrays": True
            }
        },
        # 从bp获取数据
        {
            "$lookup": {
                "from": "bp",  # 假设db_bp中的集合名
                "localField": "user_id",
                "foreignField": "id",
                "as": "bp_data"
            }
        },
        {
            "$unwind": {
                "path": "$bp_data",
                "preserveNullAndEmptyArrays": True
            }
        },
    ]

    result = list(db_bind.aggregate(pipeline))

    db_yesterday.drop()

    for item in result:
        db_yesterday.insert(item)

    return 'success'