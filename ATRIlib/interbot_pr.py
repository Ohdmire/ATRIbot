from ATRIlib.Config.path_config import cover_path
from ATRIlib.DRAW import draw_rctpp
from ATRIlib.Config import path_config
from ATRIlib.API.PPYapiv2 import get_user_recentscore_info_stable
from ATRIlib.PP.Rosu import fetch_beatmap_file_async_one,calculate_pp_if_all_stable
from ATRIlib.TOOLS.CommonTools import calculate_rank_for_stable

from ATRIlib.interbot_untils import convert_mapjson,convert_userjson,convert_recinfo

# mapjson = {'beatmapset_id': '1086772', 'beatmap_id': '2272608', 'approved': '1', 'total_length': '86',
#                'hit_length': '85', 'version': 'Angel',
#                'file_md5': 'a3689f6595911caf32ab8329c6d9c378', 'diff_size': '4', 'diff_overall': '8',
#                'diff_approach': '9.1', 'diff_drain': '5.7',
#                'mode': '0', 'count_normal': '247', 'count_slider': '120', 'count_spinner': '0',
#                'submit_date': '2019-12-31 15:21:07', 'approved_date': '2020-03-28 17:02:07',
#                'last_update': '2020-03-19 13:59:55', 'artist': 'HoneyWorks', 'artist_unicode': 'HoneyWorks',
#                'title': 'Watashi no Tenshi feat. Narumi Sena (CV: Amamiya Sora)',
#                'title_unicode': 'ワタシノテンシ feat. 成海聖奈（CV：雨宮天）', 'creator': 'C O N N E R',
#                'creator_id': '3222353', 'bpm': '168', 'source': '',
#                'tags': 'short ver my little angel very very cute sister imouto mona gom [_lost_] conner c_o_n_n_e_r frozz fzl_17 hikan xen xenon- xehn serizawa haruki j_a_c_k jack japanese jpop pop j-pop',
#                'genre_id': '5', 'language_id': '3', 'favourite_count': '285', 'rating': '9.3888', 'storyboard': '0',
#                'video': '0', 'download_unavailable': '0',
#                'audio_unavailable': '0', 'playcount': '235053', 'passcount': '42534', 'packs': 'S876',
#                'max_combo': '487', 'diff_aim': '2.38286', 'diff_speed': '2.23119',
#                'difficultyrating': '4.79777'}
#
# recinfo = {'score_id': '3727585910', 'score': '2238828', 'username': 'interbot', 'maxcombo': '487', 'count50': '0',
#            'count100': '6', 'count300': '361', 'countmiss': '0', 'countkatu': '6', 'countgeki': '67',
#            'perfect': '1', 'enabled_mods': ['NF','CL'],
#            'user_id': '11788070', 'date': '2021-06-19 09:50:36', 'rank': 'S', 'pp': '133.597',
#            'replay_available': '0','accuracy': '0.9'}
#
# userjson = {'user_id': '11788070', 'username': 'interbot', 'join_date': '2018-02-22 07:51:46',
#             'count300': '1587854',
#             'count100': '339607', 'count50': '44451', 'playcount': '5319', 'ranked_score': '2038490047',
#             'total_score': '4678155119',
#             'pp_rank': '143495', 'level': '88.9205', 'pp_raw': '3196.72', 'accuracy': '95.25702667236328',
#             'count_rank_ss': '0',
#             'count_rank_ssh': '0', 'count_rank_s': '44', 'count_rank_sh': '0', 'count_rank_a': '267',
#             'country': 'CN',
#             'total_seconds_played': '496736', 'pp_country_rank': '2356', 'events': [],
#             'avatar_url':'https://a.ppy.sh/8664033?1737041607.jpeg'}

# kwargs = {
#     "pp": 133.597,
#     "fcpp": 135.604,
#     "acpp": 180.514,
# }

async def calculate_rctpp(userstruct):

    user_id = userstruct['id']

    # 计算pr分数
    data = await get_user_recentscore_info_stable(user_id)
    if len(data) == 0:
        raise ValueError("无法找到最近游玩的成绩")
    data = data[0]

    if "great" not in data["statistics"]:
        data["statistics"]["great"] = 0
    if "ok" not in data["statistics"]:
        data["statistics"]["ok"] = 0
    if "meh" not in data["statistics"]:
        data["statistics"]["meh"] = 0
    if "miss" not in data["statistics"]:
        data["statistics"]["miss"] = 0

    if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
        # 永久保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

        ppresult = await calculate_pp_if_all_stable(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"],data["statistics"], Temp=False)
    else:
        # 临时保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=True)

        ppresult = await calculate_pp_if_all_stable(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"],data["statistics"], Temp=True)

    data['mods'] = [m for m in data['mods'] if m["acronym"] != "CL"]

    stb_rank = calculate_rank_for_stable(data["statistics"]["great"], data["statistics"]["ok"], data["statistics"]["meh"], data["statistics"]["miss"])

    has_hd_or_fl = any(m["acronym"] in {"HD", "FL"} for m in data['mods'])

    if has_hd_or_fl:
        if stb_rank == "S":
            stb_rank = "SH"
        elif stb_rank == "SS":
            stb_rank = "XH"

    data["rank"] = stb_rank


    mapjson = convert_mapjson(data)
    recinfo = convert_recinfo(data)
    userjson = convert_userjson(userstruct)


    kwargs = {
        "pp": recinfo["pp"] if recinfo["pp"] != 0 else ppresult["pp"],
        "fcpp": ppresult['fcpp'],
        "acpp": ppresult['100fcpp'],
    }


    result = await draw_rctpp.drawRec(mapjson, recinfo, recinfo, userjson, debug=0, **kwargs)

    return result






