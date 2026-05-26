import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from io import BytesIO

from ATRIlib.activity import get_activity
from ATRIlib.addpp import calculate_if_get_pp
from ATRIlib.API.PPPapi import get_token_ppp, get_user_ppp_info
from ATRIlib.API.PPYapiv2 import (
    get_beatmap_info,
    get_token,
    get_user_passrecent_info,
    get_user_recentscore_info_stable,
)
from ATRIlib.avg import calculate_avg_pp, calculate_avg_pt, calculate_avg_tth
from ATRIlib.avgstar import calculate_avg_star
from ATRIlib.beatmapranking import (
    BRKUP_CACHE_DURATION,
    brkup_cache,
    calculate_beatmapranking,
    calculate_beatmapranking_update,
)
from ATRIlib.beatmaptype import calculate_beatmap_type_ba
from ATRIlib.bind import update_bind_info
from ATRIlib.bpsim import calculate_bpsim
from ATRIlib.changelog import calculate_changelog_draw, get_changelog_status
from ATRIlib.choke import calculate_choke_pp
from ATRIlib.DB.pipeline_medal import get_user_special_medal_list_from_db
from ATRIlib.DRAW.draw_medal import draw_special_medal
from ATRIlib.finddiff import find_diff, find_diff_details
from ATRIlib.github import get_commit_content
from ATRIlib.group import update_group_info
from ATRIlib.help import get_help
from ATRIlib.interbot_bd import calculate_bd
from ATRIlib.interbot_pr import calculate_rctpp
from ATRIlib.interbot_rctpp import calculate_rctpp_text
from ATRIlib.interbot_test import check2, health_check, skill, skillvs
from ATRIlib.joindate import calculate_joindate
from ATRIlib.lazerupdate import get_lazer_update
from ATRIlib.medal import (
    calculate_medal,
    calculate_medal_pr,
    calculate_medal_search,
    calculate_special_medal,
    calculate_uu_medal,
    download_all_medals,
)
from ATRIlib.monitor import monitor_profile
from ATRIlib.most_played import get_most_played
from ATRIlib.myjobs import (
    job_compress_score_database,
    job_shift_database,
    job_update_all_bind_user_bps,
    job_update_all_bind_user_info,
    job_update_all_user_bp,
    job_update_all_user_info,
    job_update_group_user_bps,
    job_update_group_user_info,
)
from ATRIlib.news import calculate_news
from ATRIlib.profile import calculate_profile
from ATRIlib.pttpp import calculate_ptt_pp
from ATRIlib.replay_similarity import (
    calculate_group_replay_similarity,
    calculate_replay_similarity,
)
from ATRIlib.score import calculate_pr_score, calculate_score, update_scores_to_db
from ATRIlib.tdba import calculate_tdba, calculate_tdba_sim
from ATRIlib.TOOLS.CommonTools import sort_dict_by_value
from ATRIlib.update import update_user_avatar
from ATRIlib.whatif import calculate_pp, calculate_rank
from utils import get_bpstruct, get_userstruct_automatically


async def cleanup_brk_cache():
    """Removes expired entries from the brkup_cache."""
    logging.info("Cleaning up brkup_cache...")
    current_time = datetime.now()
    keys_to_remove = [
        key
        for key, (cached_time, _) in brkup_cache.items()
        if current_time - cached_time > BRKUP_CACHE_DURATION
    ]
    for key in keys_to_remove:
        del brkup_cache[key]
        logging.info(f"Removed expired brkup cache entry for key: {key}")
    logging.info("Brkup cache cleanup finished.")


def format_help():

    raw = get_help()

    return raw


def format_token_ppp():

    get_token_ppp()

    return "success"


def format_token():

    get_token()

    return "success"


async def format_test1(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    bpstruct = await get_bpstruct(user_id)

    raw = health_check(userstruct, bpstruct)

    return raw


async def format_test2(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = check2(userstruct)

    return raw


async def format_skill(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    ppp_data = await get_user_ppp_info(user_id)

    raw = skill(username, ppp_data["data"]["performances"])

    return raw


async def format_skill_vs(qq_id, vs_qq_id, osuname, vsname):
    userstruct1 = await get_userstruct_automatically(qq_id, osuname)
    userstruct2 = await get_userstruct_automatically(vs_qq_id, vsname, isOther=True)
    user1_id = userstruct1["id"]
    user1name = userstruct1["username"]

    user2_id = userstruct2["id"]
    user2name = userstruct2["username"]

    ppp_data1 = await get_user_ppp_info(user1_id)

    ppp_data2 = await get_user_ppp_info(user2_id)

    raw = skillvs(
        user1name,
        ppp_data1["data"]["performances"],
        user2name,
        ppp_data2["data"]["performances"],
    )

    return raw


async def format_rctpp(qq_id, osuname, index):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    # 计算pr分数
    data = await get_user_recentscore_info_stable(user_id)
    if len(data) == 0:
        raise ValueError("无法找到最近游玩的成绩")
    data = data[index - 1]

    raw = await calculate_rctpp(data, userstruct)

    return raw


async def format_rctpp2(qq_id, osuname, index):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]

    # 计算pr分数
    data = await get_user_recentscore_info_stable(user_id)
    if len(data) == 0:
        raise ValueError("无法找到最近游玩的成绩")
    data = data[index - 1]

    raw = await calculate_rctpp_text(data)

    result = f"{username}\n{raw}"

    return result


async def format_bpsim(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = calculate_bpsim(user_id, pp_range)

    result_text = (
        f"{raw[0]['user_data']['username']}与其他玩家的bp相似度\nPP段:+-{pp_range}pp"
    )
    for i in raw[1:11]:
        result_text += f"\n{i['sim_count']}张 --> {i['user_data']['username']}"

    return result_text


async def format_replay_similarity(qq_id, vs_qq_id, osuname, vsname):
    userstruct1 = await get_userstruct_automatically(qq_id, osuname)
    userstruct2 = await get_userstruct_automatically(vs_qq_id, vsname, isOther=True)

    raw = await calculate_replay_similarity(userstruct1, userstruct2)
    left = raw["left"]
    right = raw["right"]
    logging.info(
        "replay similarity %s(%s score=%s bid=%s) vs %s(%s score=%s bid=%s): similarity=%.2f",
        left["username"],
        left["source"],
        left["score_id"],
        left["beatmap_id"],
        right["username"],
        right["source"],
        right["score_id"],
        right["beatmap_id"],
        raw["similarity"],
    )
    return (
        f"{left['username']} 与 {right['username']} 的 replay 轨迹\n"
        f"相似度: {raw['similarity']:.2f}%\n"
        f"https://osu.ppy.sh/scores/{left['score_id']}\n"
        f"https://osu.ppy.sh/scores/{right['score_id']}"
    )


async def format_group_replay_similarity(qq_id, group_id, osuname, group_member_list):
    if group_member_list:
        format_job_update_group_list(group_id, group_member_list)

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    raw = await calculate_group_replay_similarity(userstruct, group_id)
    if not raw["comparisons"]:
        return (
            f"{raw['base']['username']} 在本群 replay 检测\n"
            f"没有找到可比较的本地 replay，已跳过 {len(raw['skipped'])} 人"
        )
    logging.info(
        "group replay similarity %s group=%s comparisons=%s skipped=%s",
        raw["base"]["username"],
        group_id,
        len(raw["comparisons"]),
        len(raw["skipped"]),
    )
    result_text = f"{raw['base']['username']} 在本群 replay 轨迹相似度\n"
    result_text += "\n".join(
        f"{item['similarity']:.2f}%-->{item['player']['username']}"
        for item in raw["comparisons"][:10]
    )
    return result_text


def format_job_shift_database():

    raw = job_shift_database()

    return raw


async def format_joindate(qq_id, group_id, osuname, pp_range, group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id, group_member_list)

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]

    raw = calculate_joindate(user_id, group_id, pp_range)

    result_text1 = f"{username}的注册日期在本群\nPP段:+-{pp_range}pp\n"
    index = 0
    result_text2 = ""
    total_count = len(raw)
    user_rank = None

    for i in raw:
        if i["user_data"]["id"] == user_id:
            user_rank = index + 1
            break
        index += 1
    if user_rank is None:
        return f"没有在本群找到你哦"
    else:
        start_index = user_rank - 5
        end_index = user_rank + 5
        if start_index < 0:
            start_index = 0
        for i in raw[start_index:end_index]:
            joindate_format = i["user_data"]["join_date"][:10]  # 截取时间格式
            result_text2 += f"\n{joindate_format} --> {i['user_data']['username']}"
            if user_id == i["user_data"]["id"]:
                result_text2 += f" <--你在这里 "

    result_text1 += f"你的排名是{user_rank}/{total_count}"

    result_text = result_text1 + result_text2

    return result_text


async def format_avgstar(qq_id, osuname, pp_range, star_min, star_max):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    user_pp = userstruct["statistics"]["pp"]

    result = calculate_avg_star(user_id, user_pp, pp_range, star_min, star_max)

    return result


async def format_avgpp(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_pp(user_id, pp_range)

    count = round(raw[0]["count"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text = f"根据亚托莉的数据库(#{count})\n{username}对比平均PP\nPP段:{mypp}(±{pp_range})pp"
    result_text += f"\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})"
    result_text += f"\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})"
    result_text += f"\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})"
    result_text += f"\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})"
    result_text += f"\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})"
    result_text += f"\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})"
    result_text += f"\n前bp5共偏差:{diff_top5_total}pp"

    return result_text


async def format_avgpt(qq_id, osuname, pt_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_pt(user_id, pt_range)

    pt_range = round(pt_range / 60 / 60)

    count = round(raw[0]["count"])
    avgpp = round(raw[0]["avgpp"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mypt = round(userstruct["statistics"]["play_time"] / 60 / 60)
    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_pp = round(mypp - avgpp)
    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text = f"根据亚托莉的数据库(#{count})\n{username}对比平均游玩时间\nPT段:{mypt}(±{pt_range})h"
    result_text += f"\nPP:{mypp}pp -- {avgpp}pp({diff_pp})"
    result_text += f"\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})"
    result_text += f"\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})"
    result_text += f"\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})"
    result_text += f"\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})"
    result_text += f"\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})"
    result_text += f"\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})"
    result_text += f"\n前bp5共偏差:{diff_top5_total}pp"

    return result_text


async def format_avgtth(qq_id, osuname, tth_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_tth(user_id, tth_range)

    tth_range = round(tth_range / 1000)

    count = round(raw[0]["count"])
    avgpp = round(raw[0]["avgpp"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mytth = round(userstruct["statistics"]["total_hits"] / 1000)
    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_pp = round(mypp - avgpp)
    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text = f"根据亚托莉的数据库(#{count})\n{username}对比平均总打击数\nTTH段:{mytth}(±{tth_range})k"
    result_text += f"\nPP:{mypp}pp -- {avgpp}pp({diff_pp})"
    result_text += f"\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})"
    result_text += f"\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})"
    result_text += f"\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})"
    result_text += f"\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})"
    result_text += f"\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})"
    result_text += f"\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})"
    result_text += f"\n前bp5共偏差:{diff_top5_total}pp"

    return result_text


async def format_choke(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = await calculate_choke_pp(user_id)

    mypp = round(userstruct["statistics"]["pp"])
    weighted_fixed_result_total_pp = round(raw["weighted_fixed_result_total_pp"])
    total_lost_pp = round(raw["total_lost_pp"])
    total_lost_pp_plus = round(raw["total_lost_pp_plus"])

    result_text = f"{username}'s ≤0.2%miss choke"
    result_text += f"\n现在的pp:{mypp}pp({total_lost_pp})"
    result_text += f"\n如果不choke:{weighted_fixed_result_total_pp}pp"
    result_text += f"\n累加丢失的pp:{total_lost_pp_plus}pp\n"

    result_dict = sort_dict_by_value(raw["choke_dict"])

    count = 0
    for key, value in result_dict.items():
        result_text += f"bp{key + 1}:{round(value)}  "
        if (count + 1) % 2 == 0:
            result_text += f"\n"
        count += 1

    result_text += f"\n你一共choke了:{count + 1}张图\n"

    return result_text


async def format_addpp(qq_id, osuname, pp_lists):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = await calculate_if_get_pp(user_id, pp_lists)

    nowpp = round(raw["now_pp"], 2)
    newpp = round(raw["new_pp_sum"], 2)
    diff_pp = round(newpp - nowpp, 2)

    diff_rank = int(raw["original_rank"]) - int(raw["new_rank"])

    result_text = f"{username}"
    result_text += f"\n现在的pp:{nowpp}pp"
    result_text += f"\n如果加入这些pp:{newpp}pp"
    result_text += f"\n增加了:{diff_pp}pp\n"
    try:
        result_text += f"\n变化前的排名:#{int(raw['original_rank']):,}"
        result_text += f"\n变化后的排名:#{int(raw['new_rank']):,}(↑{int(diff_rank):,})"
    except:
        pass

    return result_text


async def format_pttpp(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = calculate_ptt_pp(user_id, pp_range)

    nowpp = round(raw["now_pp"], 2)
    pttpp = round(raw["ptt_pp"], 2)

    result_text = f"{username}\n"
    result_text += f"现在的pp:{nowpp}pp\n"
    result_text += f"预测的pp:{pttpp}pp"

    return result_text


async def format_brk_up(qq_id, osuname, beatmap_id, group_id):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await calculate_beatmapranking_update(user_id, beatmap_id, group_id)

    return raw


async def format_brk(qq_id, osuname, beatmap_id, group_id, mods_list, is_old):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    # 提前获取beatmap_info
    beatmap_info = await get_beatmap_info(beatmap_id)

    await update_scores_to_db(user_id, beatmap_id)
    raw = await calculate_beatmapranking_update(user_id, beatmap_id, group_id)
    result = await calculate_beatmapranking(
        user_id,
        beatmap_id,
        beatmap_info,
        group_id,
        mods_list,
        is_old,
        is_ranked=raw["is_ranked"],
    )  # Pass raw data to calculate_beatmapranking
    return result


async def format_bd(qq_id, osuname, beatmap_id, group_id, mods_list):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    # 提前获取beatmap_info
    beatmap_info = await get_beatmap_info(beatmap_id)

    await update_scores_to_db(user_id, beatmap_id)
    raw = await calculate_beatmapranking_update(user_id, beatmap_id, group_id)
    result = await calculate_bd(
        userstruct,
        user_id,
        beatmap_id,
        beatmap_info,
        group_id,
        mods_list,
        is_ranked=raw["is_ranked"],
    )  # Pass raw data to calculate_beatmapranking
    return result


async def format_update_avatar(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    avatar_url = userstruct["avatar_url"]

    raw = await update_user_avatar(user_id, avatar_url)

    result = username + raw

    return result


async def format_brkpr(qq_id, osuname, group_id, index, is_old):

    mods_list = ["None"]

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    data = await get_user_passrecent_info(user_id)
    if len(data) == 0:
        raise ValueError("无法找到最近游玩的成绩")
    data = data[index - 1]
    beatmap_id = data["beatmap_id"]

    # 提前获取beatmap_info
    beatmap_info = await get_beatmap_info(beatmap_id)

    await update_scores_to_db(user_id, beatmap_id)
    raw = await calculate_beatmapranking_update(user_id, beatmap_id, group_id)
    result = await calculate_beatmapranking(
        user_id,
        beatmap_id,
        beatmap_info,
        group_id,
        mods_list,
        is_old,
        is_ranked=raw["is_ranked"],
    )  # Pass raw data to calculate_beatmapranking
    return result


async def format_medal(medalid, cache=True):

    raw = calculate_medal(medalid, cache)

    return raw


async def format_medal_search(medal_name, cache=True):
    raw = calculate_medal_search(medal_name, cache)
    return raw


async def format_medal_pr(qq_id, osuname, index=1, cache=True):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    achievements = userstruct.get("user_achievements") or []
    if not achievements:
        raise ValueError(
            f"{userstruct.get('username', userstruct.get('id'))} 没有可读取的奖牌解锁记录"
        )

    index = int(index or 1)
    if index == 0:
        raise ValueError("index 不能为 0")

    achievements = sorted(
        achievements,
        key=lambda item: item.get("achieved_at") or "",
        reverse=True,
    )
    if abs(index) > len(achievements):
        raise ValueError(
            f"index 超出范围，该用户共有 {len(achievements)} 个奖牌解锁记录"
        )

    achievement = achievements[index - 1] if index > 0 else achievements[index]
    medalid = achievement["achievement_id"]
    raw = calculate_medal(medalid, cache)

    return raw


async def format_medal_pr_all(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_medal_pr(user_id)
    return raw


async def format_uu_medal(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_uu_medal(user_id)

    result_text = f"{userstruct['username']}的Medal"

    for achievement_name, achieved_at in raw.items():
        result_text += f"\n{achieved_at[:10]} --> {achievement_name}"

    return result_text


async def format_special_medal(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw_pass, raw_fc = await calculate_special_medal(user_id)

    img = draw_special_medal(raw_pass, raw_fc, username)

    return img


async def format_download_medal():

    raw = await download_all_medals()

    return raw


async def format_pr(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_pr_score(user_id)

    return raw


async def format_tdba(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    await get_bpstruct(user_id)

    raw = calculate_tdba(user_id)

    return raw


async def format_score(qq_id, osuname, beatmapid):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await calculate_score(user_id, beatmapid)

    return raw


async def format_tdba_sim(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]

    raw = calculate_tdba_sim(user_id)

    result_text = f"{username}的tdba相似度的相似度"

    for i in raw[:10]:
        similarity = round(i["cosineSimilarity"], 2)
        result_text += f"\n{similarity} --> {i['user_data']['username']}"

    return result_text


async def format_calculate_rank(pp):
    raw = await calculate_rank(pp)
    result_text = f"{pp}pp对应的排名为\n#{raw:,}"

    return result_text


async def format_calculate_pp(rank):
    raw = await calculate_pp(rank)

    result_text = f"#{rank:,}对应的pp为\n{raw}pp"

    return result_text


async def format_most_played_beatmap(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await get_most_played(user_id)

    return raw


async def format_finddiff(group_id, group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id, group_member_list)

    await job_update_group_user_bps(group_id)

    # await job_update_all_bind_user_bps()

    raw = find_diff(group_id)

    if raw == []:
        return "今日还没有杂鱼哦"

    result_text = "今日杂鱼排行榜"

    for i in raw[:15]:
        total_pp_difference = round(i["total_pp_difference"], 2)

        total_diff_len = len(i["details"])

        result_text += (
            f"\n{total_pp_difference}pp --> {i['username']} ({total_diff_len}张)"
        )

    if len(raw) > 15:
        result_text += f"\n......还有{len(raw) - 15}个杂鱼哦"

    return result_text


async def format_finddiff_details(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = find_diff_details(user_id)

    if raw == []:
        return f"{username}才不是杂鱼呢"

    result_text = f"杂鱼~{username}"

    for i in raw:
        diff_pp = round(i["pp_difference"], 2)
        current_pp = round(i["current_pp"], 2)
        result_text += f"\nb{i['beatmap_id']} --> {current_pp}pp({diff_pp})"

    return result_text


async def format_beatmap_type_ba(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw, count_bp = await calculate_beatmap_type_ba(user_id)

    result_text = f"{username}的bp类型"
    result_text += f"\nAim:{raw['aim_total']:.2f}% ({raw['aim_count']}张)"
    result_text += f"\nStream:{raw['stream_total']:.2f}% ({raw['stream_count']}张)"
    result_text += f"\nTech:{raw['tech_total']:.2f}% ({raw['tech_count']}张)"
    result_text += f"\nAlt:{raw['alt_total']:.2f}% ({raw['alt_count']}张)"
    if count_bp != 100:
        result_text += f"\n(只计算了{count_bp}张bp之后再试试吧)"
    return result_text


async def format_profile(qq_id, osuname, vs_qq_id, is_yesterday=False):
    if vs_qq_id is not None:
        userstruct = await get_userstruct_automatically(vs_qq_id, osuname, isOther=True)
        user_id = userstruct["id"]
    else:
        userstruct = await get_userstruct_automatically(qq_id, osuname)
        user_id = userstruct["id"]
    result = await calculate_profile(user_id, is_yesterday)
    return result


async def format_news(index, is_raw_news):
    result = await calculate_news(index, is_raw_news)
    return result


async def format_changelog_draw(stream, index, cache):
    result = await calculate_changelog_draw(stream, index, cache)
    return result


async def format_changelog_status(stream):
    stauts = await get_changelog_status(stream)
    builds = stauts["builds"]
    version = f"{builds[0]['update_stream']['name']}-{builds[0]['display_version']}"
    return version


async def format_monitor_profile(group_id, group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id, group_member_list)

    await job_update_group_user_info(group_id)

    raw = monitor_profile(group_id)

    if len(raw) == 0:
        return "今天还没有人更新profile哦 不过我会一直监视你👀"

    result_text = f"今天他悄悄的更新了profile👀"
    for i in raw[:10]:
        result_text += f"\n{i['diff_score'] * 100:.2f}% --> {i['username']}"
    if len(raw) > 10:
        result_text += f"\n......还有{len(raw) - 10}个哦 我会一直监视你👀"

    return result_text


async def format_lazer_update():

    raw = await get_lazer_update()

    utc_time = datetime.strptime(raw["published_at"], "%Y-%m-%dT%H:%M:%SZ")
    utc8_time = utc_time + timedelta(hours=8)

    result_text = f"Lazer最新版本号{raw['tag_name']}"
    result_text += f"\n发布时间:{utc8_time}"
    result_text += f"\n镜像下载链接:"
    for i in raw["proxy_url"]:
        result_text += f"\n{i}"

    return result_text


async def format_pprework_progress():
    raw = await get_commit_content()
    return raw


async def format_activity(group_id, group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id, group_member_list)

    # await job_update_group_user_info(group_id)
    # await job_update_group_user_bps(group_id)

    raw = get_activity(group_id)

    return raw


async def format_job_update_all_bind_users_info():

    raw = await job_update_all_bind_user_info()

    return raw


async def format_job_update_all_users_info():

    raw = await job_update_all_user_info()

    return raw


async def format_job_update_all_users_bp():

    raw = await job_update_all_user_bp()

    return raw


async def format_job_update_all_bind_users_bp():

    raw = await job_update_all_bind_user_bps()

    return raw


def format_job_compress_score_database():

    raw = job_compress_score_database()

    diff_time = raw["diff_time"]
    count = raw["count"]

    result_text = f"共清理{count}个重复成绩\n用时{diff_time}"

    return result_text


def format_job_update_group_list(group_id, group_members_list):

    raw = update_group_info(group_id, group_members_list)

    return raw


def format_bind(qq_id, osuname):

    raw = update_bind_info(qq_id, osuname)

    return raw
