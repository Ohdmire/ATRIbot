from datetime import datetime, timezone, timedelta



def factBpm(rawbpm, modstr):
    bpm = rawbpm
    if 'DT' in modstr or 'NC' in modstr:
        bpm = rawbpm * 1.5
    elif 'HT' in modstr:
        bpm = rawbpm * 0.75
    return round(bpm)

def convert_mapjson(data):
    beatmap = data.get('beatmap', {})
    beatmapset = data.get('beatmapset', {})

    return {
        'beatmapset_id': str(beatmapset.get('id', '')),
        'beatmap_id': str(beatmap.get('id', '')),
        'approved': '1' if beatmap.get('status') in ['ranked', 'approved'] else '0',
        'total_length': int(beatmap.get('total_length', 0)),
        'hit_length': int(beatmap.get('hit_length', 0)),
        'version': beatmap.get('version', ''),
        'diff_size': float(beatmap.get('cs', 0.0)),
        'diff_overall': float(beatmap.get('accuracy', 0.0)),
        'diff_approach': float(beatmap.get('ar', 0.0)),
        'diff_drain': float(beatmap.get('drain', 0.0)),
        'mode': '0',  # Assuming osu!standard
        'count_normal': int(beatmap.get('count_circles', 0)),
        'count_slider': int(beatmap.get('count_sliders', 0)),
        'count_spinner': int(beatmap.get('count_spinners', 0)),
        'artist': beatmapset.get('artist', ''),
        'artist_unicode': beatmapset.get('artist_unicode', ''),
        'title': beatmapset.get('title', ''),
        'title_unicode': beatmapset.get('title_unicode', ''),
        'creator': beatmapset.get('creator', ''),
        'creator_id': str(beatmapset.get('user_id', '')),
        'bpm': float(beatmap.get('bpm', 0.00)),
        'source': beatmapset.get('source', ''),
        'tags': '',
        'genre_id': '0',
        'language_id': '0',
        'difficultyrating': float(beatmap.get('difficulty_rating', 0.00)),
        'max_combo': int(data.get('max_combo', 0)),
        'playcount': int(beatmap.get('playcount', 0)),
        'passcount': int(beatmap.get('passcount', 0))
    }


def convert_beatmap_data(data):
    # 判断数据是来自mapjson还是API格式
    if 'beatmap' in data and 'beatmapset' in data:
        # mapjson格式处理
        beatmap = data.get('beatmap', {})
        beatmapset = data.get('beatmapset', {})
        max_combo = data.get('max_combo', 0)
    else:
        # API格式处理
        beatmap = data
        beatmapset = data.get('beatmapset', {})
        max_combo = beatmap.get('max_combo', 0)

    # 统一提取字段
    status = beatmap.get('status', '')
    approved = '1' if status in ['ranked', 'approved'] else '0'

    return {
        'beatmapset_id': str(beatmapset.get('id', beatmap.get('beatmapset_id', ''))),
        'beatmap_id': str(beatmap.get('id', '')),
        'approved': approved,
        'total_length': int(beatmap.get('total_length', 0)),
        'hit_length': int(beatmap.get('hit_length', 0)),
        'version': beatmap.get('version', ''),
        'diff_size': float(beatmap.get('cs', 0.0)),
        'diff_overall': float(beatmap.get('accuracy', 0.0)),
        'diff_approach': float(beatmap.get('ar', 0.0)),
        'diff_drain': float(beatmap.get('drain', 0.0)),
        'mode': '0',  # 默认osu!standard
        'count_normal': int(beatmap.get('count_circles', 0)),
        'count_slider': int(beatmap.get('count_sliders', 0)),
        'count_spinner': int(beatmap.get('count_spinners', 0)),
        'artist': beatmapset.get('artist', ''),
        'artist_unicode': beatmapset.get('artist_unicode', ''),
        'title': beatmapset.get('title', ''),
        'title_unicode': beatmapset.get('title_unicode', ''),
        'creator': beatmapset.get('creator', ''),
        'creator_id': str(beatmapset.get('user_id', '')),
        'bpm': float(beatmap.get('bpm', 0.00)),
        'source': beatmapset.get('source', ''),
        'tags': beatmapset.get('tags', ''),
        'genre_id': str(beatmapset.get('genre_id', '0')),
        'language_id': str(beatmapset.get('language_id', '0')),
        'difficultyrating': float(beatmap.get('difficulty_rating', 0.00)),
        'max_combo': int(max_combo),
        'playcount': int(beatmap.get('playcount', 0)),
        'passcount': int(beatmap.get('passcount', 0))
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
        'score': int(data.get('legacy_total_score', 0)),
        'username': data.get('user', {}).get('username', ''),
        'maxcombo': int(data.get('max_combo', 0)),
        'count50': int(stats.get('meh', 0)),
        'count100': int(stats.get('ok', 0)),
        'count300': int(stats.get('great', 0)),
        'countmiss': int(stats.get('miss', 0)),
        'countkatu': '0',  # Not available in new format
        'countgeki': '0',  # Not available in new format
        'perfect': '1' if data.get('legacy_perfect', False) else '0',
        'enabled_mods': [mod['acronym'] for mod in data.get('mods', [])],
        'user_id': str(data.get('user_id', '')),
        'date': ended_at_utc8,
        'rank': data.get('rank', ''),
        'pp': 0 if data.get('pp', 0) is None else float(data.get('pp', 0.00)),
        'replay_available': '1' if data.get('has_replay', False) else '0',
        'accuracy': float(data.get('accuracy', 0.00))
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
