from ATRIlib.DB.Mongodb import db_bind,db_group

def get_group_users_id_list(group_id):

    group_info = db_group.find_one({'id': group_id})
    
    group_qq_id_list = group_info['qq_id_list']

    pipeline = [
        {'$match': {'id': {'$in': group_qq_id_list}}},
    ]

    raw = db_bind.aggregate(pipeline)

    # 使用列表推导式替代 for 循环
    users_id_list = [i['user_id'] for i in raw]

    return users_id_list

