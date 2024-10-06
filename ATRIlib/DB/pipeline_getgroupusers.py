from ATRIlib.DB.Mongodb import db_bind,db_group

def get_group_users_id_list(group_id):

    users_id_list = []

    group_info = db_group.find_one({'id': group_id})
    
    group_qq_id_list = group_info['qq_id_list']

    pipeline = [
        {'$match': {'id': {'$in': group_qq_id_list}}},
    ]

    raw = db_bind.aggregate(pipeline)

    for i in raw:

        users_id_list.append(i['user_id'])

    return users_id_list

