import logging

from ATRIlib.bpsim import calculate_bpsim
from ATRIlib.joindate import calculate_joindate
from ATRIlib.avg import calculate_avg_pp,calculate_avg_pt,calculate_avg_tth
from ATRIlib.choke import calculate_choke_pp
from utils import get_userstruct_automatically,get_bpstruct
from ATRIlib.TOOLS.CommonTools import sort_dict_by_value
from ATRIlib.addpp import calculate_if_get_pp
from ATRIlib.score import calculate_pr_score,calculate_score,update_scores_to_db
from ATRIlib.pttpp import calculate_ptt_pp
from ATRIlib.tdba import calculate_tdba
from ATRIlib.tdba import calculate_tdba_sim

from ATRIlib.beatmapranking import calculate_beatmapranking,calculate_beatmapranking_update

from ATRIlib.myjobs import job_update_all_bind_user_info,job_compress_score_database,job_update_all_bind_user_bps
from ATRIlib.myjobs import job_update_all_user_info,job_update_all_user_bp

from ATRIlib.myjobs import job_shift_database,job_update_group_user_info,job_update_group_user_bps

from ATRIlib.group import update_group_info

from ATRIlib.bind import update_bind_info

from ATRIlib.interbot import get_interbot_test1,get_interbot_test2,get_interbot_skill

from ATRIlib.API.PPYapiv2 import get_token
from ATRIlib.whatif import calculate_pp,calculate_rank

from ATRIlib.medal import calculate_medal, download_all_medals, calculate_medal_pr,calculate_uu_medal,calculate_special_medal

from ATRIlib.help import get_help

from ATRIlib.most_played import get_most_played

from ATRIlib.finddiff import find_diff,find_diff_details

from ATRIlib.activity import get_activity

from ATRIlib.beatmaptype import calculate_beatmap_type_ba

from ATRIlib.profile import calculate_profile

from ATRIlib.monitor import monitor_profile

from ATRIlib.lazerupdate import get_lazer_update

from ATRIlib.DRAW.draw_medal import draw_special_medal
from ATRIlib.DB.pipeline_medal import get_user_special_medal_list_from_db

from ATRIlib.news import calculate_news

from ATRIlib.github import get_commit_content

from io import BytesIO

import traceback
import asyncio
from asyncio import Semaphore


profile_semaphore = Semaphore(1)  # 限制为1表示一次只能处理一个请求


def handle_exceptions(func):
    if asyncio.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            try:
                s_result = await func(*args, **kwargs)
                logging.info(f'[{func.__name__}] <args:{args}>\n <kwargs:{kwargs}>\n{s_result}')
                return s_result
            except Exception as e:
                error_message = f"An error occurred in {func.__name__}:\n <args:{args}>\n <kwargs:{kwargs}>\n"
                error_message += traceback.format_exc()
                logging.error(error_message)
                if type(e) == ValueError:
                    return str(e)
                else:
                    logging.error("Unexpected error")
                    return "发生了预期外的错误"
    else:
        def wrapper(*args, **kwargs):
            try:
                s_result = func(*args, **kwargs)
                logging.info(s_result)
                return s_result
            except Exception as e:
                error_message = f"An error occurred in {func.__name__}:\n"
                error_message += traceback.format_exc()
                logging.error(error_message)
                if type(e) == ValueError:
                    return str(e)
                else:
                    logging.error("Unexpected error")
                    return "发生了预期外的错误"
    return wrapper

@handle_exceptions
def format_help():

    raw = get_help()

    return raw

@handle_exceptions
def format_token():

    get_token()

    return 'success'

@handle_exceptions
async def format_test1(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]

    raw = await get_interbot_test1(username)

    if "王者" in raw:
        raw = raw.replace("王者","老登")

    return raw


@handle_exceptions
async def format_test2(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]

    raw = await get_interbot_test2(username)

    return raw

@handle_exceptions
async def format_skill(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]

    raw = await get_interbot_skill(username)

    return raw

@handle_exceptions
async def format_bpsim(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = calculate_bpsim(user_id,pp_range)

    result_text = f'{raw[0]["user_data"]["username"]}与其他玩家的bp相似度\nPP段:+-{pp_range}pp'
    for i in raw[1:11]:
        result_text += f'\n{i["sim_count"]}张 --> {i["user_data"]["username"]}'

    return result_text

@handle_exceptions
def format_job_shift_database():

    raw = job_shift_database()

    return raw

@handle_exceptions
async def format_joindate(qq_id, group_id, osuname, pp_range,group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id,group_member_list)

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username= userstruct["username"]

    raw = calculate_joindate(user_id, group_id, pp_range)

    result_text1 = f'{username}的注册日期在本群\nPP段:+-{pp_range}pp\n'
    index = 0
    result_text2 = ''
    total_count = len(raw)
    user_rank = None

    for i in raw:
        if i["user_data"]["id"] == user_id:
            user_rank = index + 1
            break
        index += 1
    if user_rank is None:
        return f'没有在本群找到你哦'
    else:
        start_index = user_rank - 5
        end_index = user_rank +5
        if start_index < 0:
            start_index = 0
        for i in raw[start_index:end_index]:
            joindate_format = i["user_data"]["join_date"][:10] #截取时间格式
            result_text2 += f'\n{joindate_format} --> {i["user_data"]["username"]}'
            if user_id == i["user_data"]["id"]:
                result_text2 += f' <--你在这里 '

    result_text1 += f'你的排名是{user_rank}/{total_count}'

    result_text = result_text1 + result_text2

    return result_text

@handle_exceptions
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

    result_text=f'根据亚托莉的数据库(#{count})\n{username}对比平均PP\nPP段:{mypp}(±{pp_range})pp'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
async def format_avgpt(qq_id, osuname, pt_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_pt(user_id, pt_range)

    pt_range = round(pt_range/60/60)

    count = round(raw[0]["count"])
    avgpp = round(raw[0]["avgpp"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mypt = round(userstruct["statistics"]["play_time"]/60/60)
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

    result_text = f'根据亚托莉的数据库(#{count})\n{username}对比平均游玩时间\nPT段:{mypt}(±{pt_range})h'
    result_text += f'\nPP:{mypp}pp -- {avgpp}pp({diff_pp})'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
async def format_avgtth(qq_id, osuname, tth_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_tth(user_id, tth_range)

    tth_range = round(tth_range/1000)

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

    result_text = f'根据亚托莉的数据库(#{count})\n{username}对比平均游玩时间\nTTH段:{mytth}(±{tth_range})w'
    result_text += f'\nPP:{mypp}pp -- {avgpp}pp({diff_pp})'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
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

    result_text = f'{username}\'s ≤0.5%miss choke'
    result_text += f'\n现在的pp:{mypp}pp({total_lost_pp})'
    result_text += f'\n如果不choke:{weighted_fixed_result_total_pp}pp'
    result_text += f'\n累加丢失的pp:{total_lost_pp_plus}pp\n'

    result_dict = sort_dict_by_value(raw["choke_dict"])

    count = 0
    for key,value in result_dict.items():
        result_text += f'bp{key + 1}:{round(value)}  '
        if (count+1) % 2 == 0:
            result_text += f'\n'
        count += 1

    return result_text

@handle_exceptions
async def format_addpp(qq_id, osuname,pp_lists):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = await calculate_if_get_pp(user_id,pp_lists)

    nowpp = round(raw["now_pp"],2)
    newpp = round(raw["new_pp_sum"],2)
    diff_pp = round(newpp - nowpp,2)

    diff_rank = int(raw["original_rank"]) - int(raw["new_rank"])

    result_text = f'{username}'
    result_text += f'\n现在的pp:{nowpp}pp'
    result_text += f'\n如果加入这些pp:{newpp}pp'
    result_text += f'\n增加了:{diff_pp}pp\n'
    result_text += f'\n变化前的排名:#{int(raw["original_rank"]):,}'
    result_text += f'\n变化后的排名:#{int(raw["new_rank"]):,}(↑{int(diff_rank):,})'

    return result_text

@handle_exceptions
async def format_pttpp(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = calculate_ptt_pp(user_id,pp_range)

    nowpp = round(raw['now_pp'],2)
    pttpp = round(raw['ptt_pp'],2)

    result_text = f'{username}\n'
    result_text += f'现在的pp:{nowpp}pp\n'
    result_text += f'预测的pp:{pttpp}pp'

    return result_text


@handle_exceptions
async def format_brk_up(beatmap_id,group_id):

    raw = await calculate_beatmapranking_update(beatmap_id,group_id)

    return raw


@handle_exceptions
async def format_brk(qq_id, osuname,beatmap_id,group_id,mods_list,is_old):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    await update_scores_to_db(user_id, beatmap_id)

    raw = await calculate_beatmapranking(user_id,beatmap_id,group_id,mods_list,is_old)

    return raw

@handle_exceptions
async def format_medal(medalid):

    raw = calculate_medal(medalid)

    return raw

@handle_exceptions
async def format_medal_pr(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_medal_pr(user_id)

    return raw

@handle_exceptions
async def format_uu_medal(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_uu_medal(user_id)

    result_text = f'{userstruct["username"]}的Medal'

    for achievement_name,achieved_at in raw.items():
        result_text += f'\n{achieved_at[:10]} --> {achievement_name}'    

    return result_text

@handle_exceptions
async def format_special_medal(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw_pass,raw_fc = await calculate_special_medal(user_id)
    
    img = draw_special_medal(raw_pass,raw_fc,username)

    return img

@handle_exceptions
async def format_download_medal():

    raw = await download_all_medals()

    return raw


@handle_exceptions
async def format_pr(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_pr_score(user_id)

    return raw

@handle_exceptions
async def format_tdba(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    await get_bpstruct(user_id)

    raw = calculate_tdba(user_id)

    return raw


@handle_exceptions
async def format_score(qq_id, osuname,beatmapid):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await calculate_score(user_id,beatmapid)

    return raw


@handle_exceptions
async def format_tdba_sim(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]

    raw = calculate_tdba_sim(user_id)

    result_text = f'{username}的tdba相似度的相似度'

    for i in raw[:10]:
        similarity = round(i['cosineSimilarity'],2)
        result_text += f'\n{similarity} --> {i["user_data"]["username"]}'

    return result_text

@handle_exceptions
async def format_calculate_rank(pp):
    raw = await calculate_rank(pp)
    result_text = f'{pp}pp对应的排名为\n#{raw:,}'

    return result_text

@handle_exceptions
async def format_calculate_pp(rank):
    raw = await calculate_pp(rank)

    result_text = f'#{rank:,}对应的pp为\n{raw}pp'

    return result_text


@handle_exceptions
async def format_most_played_beatmap(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await get_most_played(user_id)

    return raw

@handle_exceptions
async def format_finddiff(group_id,group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id,group_member_list)

    await job_update_group_user_bps(group_id)

    # await job_update_all_bind_user_bps()

    raw = find_diff(group_id)

    if raw == []:
        return '今日还没有杂鱼哦'

    result_text = '今日杂鱼排行榜'

    for i in raw[:15]:

        total_pp_difference = round(i["total_pp_difference"],2)

        total_diff_len = len(i["details"])

        result_text += f'\n{total_pp_difference}pp --> {i["username"]} ({total_diff_len}张)'
    
    if len(raw) > 15:
        result_text += f'\n......还有{len(raw)-15}个杂鱼哦'

    return result_text

@handle_exceptions
async def format_finddiff_details(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = find_diff_details(user_id)

    if raw == []:
        return f'{username}才不是杂鱼呢'

    result_text = f'杂鱼~{username}'

    for i in raw:
        diff_pp = round(i["pp_difference"],2)
        current_pp = round(i["current_pp"],2)
        result_text += f'\nb{i["beatmap_id"]} --> {current_pp}pp({diff_pp})'

    return result_text

@handle_exceptions
async def format_beatmap_type_ba(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw,count_bp = await calculate_beatmap_type_ba(user_id)

    result_text = f'{username}的bp类型'
    result_text += f'\nAim:{raw["aim_total"]:.2f}% ({raw["aim_count"]}张)'
    result_text += f'\nStream:{raw["stream_total"]:.2f}% ({raw["stream_count"]}张)'
    result_text += f'\nTech:{raw["tech_total"]:.2f}% ({raw["tech_count"]}张)'
    result_text += f'\nAlt:{raw["alt_total"]:.2f}% ({raw["alt_count"]}张)'
    if count_bp != 100:
        result_text += f'\n(只计算了{count_bp}张bp之后再试试吧)'
    return result_text

@handle_exceptions
async def format_profile(qq_id, osuname,is_yesterday=False):
    # 使用信号量控制并发
    async with profile_semaphore:
        userstruct = await get_userstruct_automatically(qq_id, osuname)
        user_id = userstruct["id"]
        result = await calculate_profile(user_id,is_yesterday)
        return result

@handle_exceptions
async def format_news(index,is_raw_news):
    # 使用信号量控制并发
    async with profile_semaphore:
        result = await calculate_news(index,is_raw_news)
        return result

@handle_exceptions
async def format_monitor_profile(group_id,group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id,group_member_list)

    await job_update_group_user_info(group_id)

    raw = monitor_profile(group_id)

    if len(raw) == 0:
        return '今天还没有人更新profile哦 不过我会一直监视你👀'

    result_text = f'今天他悄悄的更新了profile👀'
    for i in raw[:10]:
        result_text += f'\n{i["diff_score"]*100:.2f}% --> {i["username"]}'
    if len(raw) > 10:
        result_text += f'\n......还有{len(raw)-10}个哦 我会一直监视你👀'

    return result_text

@handle_exceptions
async def format_lazer_update():

    raw = await get_lazer_update()

    result_text = f'Lazer最新版本号{raw["tag_name"]}'
    result_text += f'\n发布时间:{raw["published_at"]}'
    result_text += f'\n镜像下载链接:'
    for i in raw['proxy_url']:
        result_text += f'\n{i}'

    return result_text

@handle_exceptions
async def format_pprework_progress():
    raw = await get_commit_content()
    return raw

@handle_exceptions
async def format_activity(group_id,group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id,group_member_list)

    # await job_update_group_user_info(group_id)
    # await job_update_group_user_bps(group_id)

    raw = get_activity(group_id)

    return raw

@handle_exceptions
async def format_job_update_all_bind_users_info():

    raw = await job_update_all_bind_user_info()

    return raw

@handle_exceptions
async def format_job_update_all_users_info():

    raw = await job_update_all_user_info()

    return raw

@handle_exceptions
async def format_job_update_all_users_bp():

    raw = await job_update_all_user_bp()

    return raw

@handle_exceptions
async def format_job_update_all_bind_users_bp():

    raw = await job_update_all_bind_user_bps()

    return raw


@handle_exceptions
def format_job_compress_score_database():

    raw = job_compress_score_database()

    diff_time = raw['diff_time']
    count = raw['count']

    result_text = f'共清理{count}个重复成绩\n用时{diff_time}'

    return result_text


@handle_exceptions
def format_job_update_group_list(group_id,group_members_list):

    raw = update_group_info(group_id,group_members_list)

    return raw


@handle_exceptions
def format_bind(qq_id, osuname):

    raw = update_bind_info(qq_id,osuname)

    return raw







