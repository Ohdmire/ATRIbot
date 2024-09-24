from ATRIlib.DB.Mongodb import update_db_group

# 更新group
def update_group(group_id, members_list):

    update_db_group(group_id, members_list)