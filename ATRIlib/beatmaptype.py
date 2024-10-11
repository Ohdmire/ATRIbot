from ATRIlib.DB.Mongodb import db_bp, db_beatmaptype

def calculate_beatmap_type_ba(user_id):

    bpinfo = db_bp.find_one({"id": user_id})
    bps_beatmap_id_list = bpinfo["bps_beatmapid"]

    raw = {}

    raw["aim_total"] = 0
    raw["stream_total"] = 0
    raw["tech_total"] = 0
    raw["alt_total"] = 0

    raw["aim_count"] = 0
    raw["stream_count"] = 0
    raw["tech_count"] = 0
    raw["alt_count"] = 0

    for bps_beatmap_id in bps_beatmap_id_list:
        beatmap_type = db_beatmaptype.find_one({"beatmap_id": bps_beatmap_id})
        # 如果存在且不为0
        if beatmap_type:
            raw["aim_total"] += beatmap_type["aim"]
            raw["stream_total"] += beatmap_type["stream"]
            raw["tech_total"] += beatmap_type["tech"]
            raw["alt_total"] += beatmap_type["alt"]
            if beatmap_type["aim"] != 0:
                raw["aim_count"] += 1
            if beatmap_type["stream"] != 0:
                raw["stream_count"] += 1
            if beatmap_type["tech"] != 0:
                raw["tech_count"] += 1
            if beatmap_type["alt"] != 0:
                raw["alt_count"] += 1
        else:
            return "无法找到谱面类型"

    return raw
