from ATRIlib.DB.mongodb import db_bp, db_beatmaptype
# 第一步 首先先获取bps_beatmap_id

def calculate_beatmap_type(user_id):
    bpinfo = db_bp.find_one({"user_id": user_id})
    bps_beatmap_id = bpinfo["bps_beatmapid"]

    # 第二部 批量查询db_beatmaptype里是否存在数据 返回没有的
    beatmap_type_list = db_beatmaptype.find({"beatmap_id": bps_beatmap_id})
    for i in beatmap_type_list:
        if i["aim"] == 0 and i["stream"] == 0 and i["tech"] == 0 and i["alt"] == 0:
            return "无法找到该谱面"
