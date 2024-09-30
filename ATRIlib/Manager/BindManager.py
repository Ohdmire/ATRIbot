from ATRIlib.DB.Mongodb import db_bind, update_db_bind, db_user


# 查找绑定
def find_bind(qq_id):
    bind = db_bind.find_one({'id': qq_id})
    return bind


# 解绑
def delete_bind(qq_id):
    try:
        db_bind.delete({"id": qq_id})
        return True
    except:
        return False


# 更新绑定
def update_bind(qq_id,userdata):
    bind_info = db_bind.find_one({'id': qq_id})
    if bind_info is not None:
        userstruct = db_user.find_one({'id': bind_info["user_id"]})
        return f'你已绑定{userstruct["username"]}如需解绑请联系管理员'
    else:
        bind_info = db_bind.find_one({'user_id': userdata["id"]})
        if bind_info is not None:
            return f'{userdata["username"]}已经被绑定'
        else:
            update_db_bind(qq_id, userdata)
            return f'{userdata["username"]}绑定成功'