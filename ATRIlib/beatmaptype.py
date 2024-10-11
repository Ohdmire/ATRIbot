from ATRIlib.DB.Mongodb import db_bp, db_beatmaptype
from ATRIlib.API.Customapi import get_beatmap_type
from ATRIlib.Manager.BeatmapTypeManager import update_beatmap_attributes


async def calculate_beatmap_type_ba(user_id):

    count_bp = 0

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

    lack_beatmap_id_list = []

    for bps_beatmap_id in bps_beatmap_id_list:
        beatmap_type = db_beatmaptype.find_one({"id": bps_beatmap_id})
        if beatmap_type:
            count_bp += 1
            if "aim" in beatmap_type:
                raw["aim_total"] += beatmap_type["aim"]
                if beatmap_type["aim"] >0.5:
                    raw["aim_count"] += 1
            if "stream" in beatmap_type:
                raw["stream_total"] += beatmap_type["stream"]
                if beatmap_type["stream"] >0.5:
                    raw["stream_count"] += 1
            if "tech" in beatmap_type:
                raw["tech_total"] += beatmap_type["tech"]
                if beatmap_type["tech"] >0.5:
                    raw["tech_count"] += 1
            if "alt" in beatmap_type:
                raw["alt_total"] += beatmap_type["alt"]
                if beatmap_type["alt"] >0.5:
                    raw["alt_count"] += 1
        else:
            lack_beatmap_id_list.append(bps_beatmap_id)

    if lack_beatmap_id_list:
        get_beatmap_type_data = await get_beatmap_type(lack_beatmap_id_list)
        for beatmap_id,beatmap_type in get_beatmap_type_data.items():
            update_beatmap_attributes(beatmap_id,beatmap_type)
            count_bp += 1
            if "aim" in beatmap_type:
                raw["aim_total"] += beatmap_type["aim"]
                if beatmap_type["aim"] >0.5:
                    raw["aim_count"] += 1
            if "stream" in beatmap_type:
                raw["stream_total"] += beatmap_type["stream"]
                if beatmap_type["stream"] >0.5:
                    raw["stream_count"] += 1
            if "tech" in beatmap_type:
                raw["tech_total"] += beatmap_type["tech"]
                if beatmap_type["tech"] >0.5:
                    raw["tech_count"] += 1
            if "alt" in beatmap_type:
                raw["alt_total"] += beatmap_type["alt"]
                if beatmap_type["alt"] >0.5:
                    raw["alt_count"] += 1

    return raw,count_bp
