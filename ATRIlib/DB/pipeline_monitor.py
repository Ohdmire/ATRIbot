from ATRIlib.DB.Mongodb import db_bind,db_group

def monitor_pipeline(group_id):

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
        {"$lookup": {
            "from": "user",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_data"
        }},
        {"$unwind": "$user_data"},
        
        # 添加比较page.raw数据的步骤
        {"$match": {
            "$expr": {
                "$ne": ["$yesterday_data.user_data.page.raw", "$user_data.page.raw"]
            }
        }},
        
        # 输出需要的字段
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "username": "$user_data.username",
            "old_page_raw": "$yesterday_data.user_data.page.raw",
            "new_page_raw": "$user_data.page.raw"
        }}
    ]

    return list(db_bind.aggregate(pipeline))