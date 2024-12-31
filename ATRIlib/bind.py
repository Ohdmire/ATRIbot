from ATRIlib.API.PPYapiv2  import get_user_info
from ATRIlib.Manager.BindManager import update_bind,find_bind
from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.Manager.UserManager import update_user
from ATRIlib.info import update_user_info


# 更新bind
async def update_bind_info(qq_id,osuname):
    userdata = await get_user_info(osuname)
    if 'id' in userdata:
        update_user(userdata)
        return update_bind(qq_id, userdata)
    else:
        raise ValueError(f'无法在ppy的数据库中找到{osuname}')

# 通过bind数据库获取userstruct
def get_userstruct_from_bind(qq_id):
    bindstruct = find_bind(qq_id)
    if bindstruct is None:
        raise ValueError(f'无法在数据库中找到qq={qq_id}绑定的对象\n尝试输入 !getbind')
    else:
        userstruct = db_user.find_one({'id': bindstruct["user_id"]})
        return userstruct

async def get_userstrct_update_from_bind(qq_id):
    userstruct = get_userstruct_from_bind(qq_id)
    if userstruct is None:
        raise ValueError(f'无法在数据库中找到qq={qq_id}绑定的对象\n尝试输入 !getbind')
    else:
        userstruct = await update_user_info(userstruct['username'])
        return userstruct
# 通过bind数据库获取bpstruct
def get_bpstruct_from_bind(qq_id):
    bindstruct = find_bind(qq_id)
    if bindstruct is None:
        return None
    else:
        bpstruct = db_bp.find_one({'id': bindstruct["user_id"]})
        return bpstruct
