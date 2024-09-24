from ATRIlib.DB.Mongodb import update_db_group

def update_group_info(group_id, member_list):

    update_db_group(group_id, member_list)

    return f'成功更新群{group_id}的{len(member_list)}个成员'