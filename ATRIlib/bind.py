from ATRIlib.API.PPYapiv2  import get_user_info
from ATRIlib.Manager.BindManager import update_bind,find_bind
from ATRIlib.DB.Mongodb import db_user,db_bp
from ATRIlib.Manager.UserManager import update_user
from ATRIlib.info import update_user_info

# 永久拉黑的osu uid，禁止绑定
blacklist = [
    7562902, 14715160, 15406985, 9269034, 10549880, 13108233, 11367222, 5033077,
    4175698, 13211727, 12779141, 12137295, 8251785, 7341183, 21207816, 17235399,
    19851850, 5199332, 6404583, 11496364, 25444680, 8640970, 9970083, 6725771,
    12834269, 13767572, 13962152, 8856806, 11626318, 8816345, 15296720, 16817965,
    10077431, 9642774, 9938943, 17730661, 13051015, 12258658, 12873118, 9074780,
    12952320, 8356568, 11443437, 9224078, 12408961, 13216706, 4108547, 10933605,
    13057699, 6600930, 5339515, 14215850, 7525949, 11159039, 10651184, 4504101,
    14106450, 9849451, 2675255, 13609904, 10323184, 2766034, 8799923, 2165650,
    8007528, 13300203, 17104779, 8868635, 19072684, 3717598, 24409289, 7813296,
    11885405, 7918057, 11592896, 2291265, 7342622, 2094566, 11415687, 7512553,
    11806306, 14676719, 12130906, 16320893, 11552867, 12434652, 1719471, 4209965,
    10760701, 2558286, 10743390, 30751112, 5981005, 9993348, 20120615, 6937470,
    6114695, 6788821, 6304246, 9896317, 8660293, 12169267, 124493, 4882979,
    8075782, 21619075, 7959222, 11243772, 11215030, 4787150, 11375105,
]


def is_blacklisted(user_id):
    return str(user_id) in {str(item) for item in blacklist}


# 更新bind
async def update_bind_info(qq_id,osuname):
    userdata = await get_user_info(osuname)
    if 'id' in userdata:
        if is_blacklisted(userdata["id"]):
            return ""

        update_user(userdata)
        return update_bind(qq_id, userdata)
    else:
        raise ValueError(f'无法在ppy的数据库中找到{osuname}')

# 通过bind数据库获取userstruct
def get_userstruct_from_bind(qq_id,isOther):
    bindstruct = find_bind(qq_id)
    if bindstruct is None:
        if isOther:
            raise ValueError("让对方绑定吧")
        raise ValueError(f'无法在数据库中找到qq={qq_id}绑定的对象\n尝试输入 !getbind')
    else:
        userstruct = db_user.find_one({'id': bindstruct["user_id"]})
        return userstruct

async def get_userstrct_update_from_bind(qq_id,isOther):
    userstruct = get_userstruct_from_bind(qq_id,isOther)
    if userstruct is None:
        if isOther:
            raise ValueError("让对方绑定吧")
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
