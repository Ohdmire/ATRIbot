from ATRIlib.Config.path_config import cover_path
from ATRIlib.DRAW import draw_rctpp
from ATRIlib.Config import path_config
from ATRIlib.API.PPYapiv2 import get_user_recentscore_info_stable
from ATRIlib.PP.Rosu import fetch_beatmap_file_async_one,calculate_pp_if_all
from ATRIlib.TOOLS.CommonTools import calculate_rank_for_stable

from datetime import datetime, timezone, timedelta


def convert_mapjson(data):
    beatmap = data.get('beatmap', {})
    beatmapset = data.get('beatmapset', {})

    return {
        'beatmapset_id': str(beatmapset.get('id', '')),
        'beatmap_id': str(beatmap.get('id', '')),
        'approved': '1' if beatmap.get('status') in ['ranked', 'approved'] else '0',
        'total_length': str(beatmap.get('total_length', '')),
        'hit_length': str(beatmap.get('hit_length', '')),
        'version': beatmap.get('version', ''),
        'diff_size': str(beatmap.get('cs', '')),
        'diff_overall': str(beatmap.get('accuracy', '')),
        'diff_approach': str(beatmap.get('ar', '')),
        'diff_drain': str(beatmap.get('drain', '')),
        'mode': '0',  # Assuming osu!standard
        'count_normal': str(beatmap.get('count_circles', '')),
        'count_slider': str(beatmap.get('count_sliders', '')),
        'count_spinner': str(beatmap.get('count_spinners', '')),
        'artist': beatmapset.get('artist', ''),
        'artist_unicode': beatmapset.get('artist_unicode', ''),
        'title': beatmapset.get('title', ''),
        'title_unicode': beatmapset.get('title_unicode', ''),
        'creator': beatmapset.get('creator', ''),
        'creator_id': str(beatmapset.get('user_id', '')),
        'bpm': str(beatmap.get('bpm', '')),
        'source': beatmapset.get('source', ''),
        'tags': '',
        'genre_id': '0',
        'language_id': '0',
        'difficultyrating': str(beatmap.get('difficulty_rating', '')),
        'max_combo': str(data.get('max_combo', '')),
        'playcount': str(beatmap.get('playcount', '')),
        'passcount': str(beatmap.get('passcount', ''))
    }


def convert_recinfo(data):
    stats = data.get('statistics', {})
    max_stats = data.get('maximum_statistics', {})

    # Handle time conversion (UTC -> UTC+8)
    ended_at_utc = data.get('ended_at', '')
    if ended_at_utc:
        try:
            utc_time = datetime.strptime(ended_at_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            utc8_time = utc_time.astimezone(timezone(timedelta(hours=8)))
            ended_at_utc8 = utc8_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            ended_at_utc8 = ended_at_utc.replace('T', ' ').replace('Z', '')
    else:
        ended_at_utc8 = ''

    return {
        'score_id': str(data.get('id', '')),
        'score': str(data.get('legacy_total_score', '')),
        'username': data.get('user', {}).get('username', ''),
        'maxcombo': str(data.get('max_combo', '')),
        'count50': str(stats.get('meh', '')),
        'count100': str(stats.get('ok', '')),
        'count300': str(stats.get('great', '')),
        'countmiss': str(stats.get('miss', '')),
        'countkatu': '0',  # Not available in new format
        'countgeki': '0',  # Not available in new format
        'perfect': '1' if data.get('legacy_perfect', False) else '0',
        'enabled_mods': [mod['acronym'] for mod in data.get('mods', [])],
        'user_id': str(data.get('user_id', '')),
        'date': ended_at_utc8,
        'rank': data.get('rank', ''),
        'pp': data.get('pp', 0),
        'replay_available': '1' if data.get('has_replay', False) else '0',
        'accuracy': str(data.get('accuracy', ''))
    }


def convert_userjson(userstruct):
    if not userstruct or len(userstruct) == 0:
        return {}

    user = userstruct
    stats = user.get('statistics', {})
    grade_counts = stats.get('grade_counts', {})

    # Handle join date conversion (UTC -> UTC+8)
    join_date_utc = user.get('join_date', '')
    if join_date_utc:
        try:
            utc_time = datetime.strptime(join_date_utc, "%Y-%m-%dT%H:%M:%S%z")
            utc8_time = utc_time.astimezone(timezone(timedelta(hours=8)))
            join_date_utc8 = utc8_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            join_date_utc8 = join_date_utc.replace('T', ' ').replace('+00:00', '')
    else:
        join_date_utc8 = ''

    return {
        'user_id': str(user.get('id', '')),
        'username': user.get('username', ''),
        'join_date': join_date_utc8,
        'count300': str(stats.get('count_300', '0')),
        'count100': str(stats.get('count_100', '0')),
        'count50': str(stats.get('count_50', '0')),
        'playcount': str(stats.get('play_count', '0')),
        'ranked_score': str(stats.get('ranked_score', {})),
        'total_score': str(stats.get('total_score', {})),
        'pp_rank': str(stats.get('global_rank', '0')),
        'level': str(stats.get('level', {}).get('current', '0')),
        'pp_raw': str(stats.get('pp', '0')),
        'accuracy': str(stats.get('hit_accuracy', '0')),
        'count_rank_ss': str(grade_counts.get('ss', '0')),
        'count_rank_ssh': str(grade_counts.get('ssh', '0')),
        'count_rank_s': str(grade_counts.get('s', '0')),
        'count_rank_sh': str(grade_counts.get('sh', '0')),
        'count_rank_a': str(grade_counts.get('a', '0')),
        'country': user.get('country_code', ''),
        'total_seconds_played': str(stats.get('play_time', '0')),
        'pp_country_rank': str(stats.get('rank', {}).get('country', '0')),
        'events': [],
        'avatar_url': user.get('avatar_url', '')
    }


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

    if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
        # 永久保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=False)
    else:
        # 临时保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=True)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=True)


    if "great" not in data["statistics"]:
        data["statistics"]["great"] = 0
    if "ok" not in data["statistics"]:
        data["statistics"]["ok"] = 0
    if "meh" not in data["statistics"]:
        data["statistics"]["meh"] = 0
    if "miss" not in data["statistics"]:
        data["statistics"]["miss"] = 0


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
        "pp": 0,
        "fcpp": ppresult['fcpp'],
        "acpp": ppresult['100fcpp'],
    }


    result = await draw_rctpp.drawRec(mapjson, recinfo, recinfo, userjson, debug=0, **kwargs)

    return result






