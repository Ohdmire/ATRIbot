from ATRIlib.DB.pipeline_beatmapranking import get_beatmapranking_list_from_db, \
    get_beatmapranking_list_from_db_old,get_beatmapranking_list_from_unrankscore_db,get_beatmapranking_list_from_unrankscore_db_old
from ATRIlib.API.PPYapiv2 import get_beatmap_info

from ATRIlib.interbot_untils import convert_mapjson,convert_recinfo,convert_userjson,convert_beatmap_data

from ATRIlib.DRAW.draw_interbot.drawRank import drawR

from ATRIlib.TOOLS.CommonTools import mods_to_str,mod_list_to_newlist

async def calculate_bd(userstruct,user_id,beatmap_id,beatmap_info,group_id,mods_list,is_ranked=True):

    if "NM" in mods_list:
        mods_list = [{
            "acronym": "CL"
        }]
    elif "None" in mods_list:
        mods_list = None
    else:
        mods_list = mod_list_to_newlist(mods_list)
        # Stable自动添加CL
        mods_list.append({"acronym": "CL"})

    if is_ranked:
        raw = get_beatmapranking_list_from_db_old(user_id, beatmap_id, group_id, mods_list)
    else:
        raw = get_beatmapranking_list_from_unrankscore_db_old(user_id, beatmap_id, group_id, mods_list)

    user_record = None
    for record in raw:
        if record["top_score"]["user_id"] == user_id:
            user_record = record
            # break
        if "great" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["great"] = 0
        if "ok" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["ok"] = 0
        if "meh" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["meh"] = 0
        if "miss" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["miss"] = 0

        record['top_score']['mods'] = [m for m in record['top_score']['mods'] if m["acronym"] != "CL"]


    # if user_record is None:
    #     user_record = {"top_score": {"user_id" : user_id , "total_score" : -1, "legacy_total_score" : -1}}

    mapjson = convert_beatmap_data(beatmap_info)
    userjson = convert_userjson(userstruct)


    result = await drawR(mapjson, raw, userjson)

    return result