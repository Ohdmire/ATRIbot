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
        'pp': 0 if data.get('pp', 0) is None else float(data.get('pp', 0)),
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
