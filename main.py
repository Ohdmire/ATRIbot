from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import BaseModel

from typing import Optional

from six import BytesIO

import ATRIproxy

import uvicorn

import logging
import logging.config

import asyncio
import os
from asyncio import Semaphore

with open('./log_config.ini', 'r', encoding='utf-8') as f:
    logging.config.fileConfig(f)

class IName(BaseModel):
    qq_id: int
    vs_qq_id: Optional[int] = None
    pp_range : Optional[int] = None
    star_min: Optional[float] = 5.00
    star_max: Optional[float] = 5.00
    osuname: Optional[str] = None
    vsname: Optional[str] = None
    pt_range: Optional[int] = None
    tth_range :Optional[int] = None
    pp_lists :Optional[list] = []
    users_id_list :Optional[list] = []
    beatmap_id : Optional[int] = None
    group_id : Optional[int] = None
    mods_list: Optional[list] = []
    group_member_list: Optional[list] = []
    is_yesterday: Optional[bool] = False
    is_old: Optional[bool] = False
    index: Optional[int] = 1

class ItemN(BaseModel):
    pp: Optional[int] = None
    rank: Optional[int] = None
    beatmap_id: Optional[int] = None
    group_id: Optional[int] = None
    group_member_list: Optional[list] = []
    medalid: Optional[int] = None
    news_index: Optional[int] = 0
    is_raw_news: Optional[bool] = True

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logging.info("亚托莉，启动!")
    
    # 定义需要创建的目录结构
    directories = [
        "data",
        "data/beatmaps",
        "data/beatmaps_tmp",
        "data/cover",
        "data/avatar",
        "logs",
        "data/tmp",
        "data/tmp/brk",
        "data/tmp/pr",
        "data/tmp/medal",
        "data/tmp/medal_pr",
        "data/tmp/profile",
        "data/tmp/news",
        "data/news",
    ]
    
    # 检查并创建目录
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"创建了 {directory} 目录")
    
    scheduler.add_job(job_fetch_token,
                      trigger="interval", seconds=3600) #定时获取token
    scheduler.add_job(job_fetch_token_ppp,
                      trigger="interval", seconds=3600)  # 定时获取ppptoken
    scheduler.add_job(job_shift_database,
                      trigger="cron", hour=4) #定时转移数据库
    scheduler.add_job(job_update_bind_all,
                      trigger="cron", hour=4,minute=2) #定时更新绑定用户所有
    scheduler.add_job(ATRIproxy.cleanup_brk_cache,
                      trigger="interval", hours=1) #定时清理brk缓存
    scheduler.start()
    yield
    logging.info("亚托莉，关闭!")

app = FastAPI(lifespan=app_lifespan)

# 限制 /qq/profile 路由的并发请求数量
profile_route_semaphore = Semaphore(1)

@app.api_route("/qq/mostplayed", methods=["GET", "POST"])
async def fetch_test2(item:IName):
    result = await ATRIproxy.format_most_played_beatmap(item.qq_id,item.osuname)
    return str(result)


@app.api_route("/help", methods=["GET", "POST"])
async def fetch_help():
    img_bytes = ATRIproxy.format_help()
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)
    
@app.api_route("/qq/beatmaptype/all", methods=["GET", "POST"])
async def fetch_beatmaptype_all(item:IName):
    result = await ATRIproxy.format_beatmap_type_ba(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/profile", methods=["GET", "POST"])
async def fetch_profile(item:IName):
    async with profile_route_semaphore:
        img_bytes = await ATRIproxy.format_profile(item.qq_id,item.osuname,item.is_yesterday)
        if type(img_bytes) is BytesIO:
            return StreamingResponse(img_bytes, media_type="image/jpeg")
        else:
            return str(img_bytes)


@app.api_route("/news", methods=["GET", "POST"])
async def fetch_news(item: ItemN):
    img_bytes = await ATRIproxy.format_news(item.news_index,item.is_raw_news)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)


@app.api_route("/qq/profile/monitor", methods=["GET", "POST"])
async def fetch_profile_monitor(item:ItemN):
    result = await ATRIproxy.format_monitor_profile(item.group_id,item.group_member_list)
    return str(result)

@app.api_route("/lazer/update", methods=["GET", "POST"])
async def fetch_lazer_update():
    result = await ATRIproxy.format_lazer_update()
    return str(result)

@app.api_route("/pprework/progress", methods=["GET", "POST"])
async def fetch_pprework_progress():
    img_bytes = await ATRIproxy.format_pprework_progress()
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/medal", methods=["GET", "POST"])
async def fetch_medal(item:ItemN):
    img_bytes = await ATRIproxy.format_medal(item.medalid)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/medal/pr", methods=["GET", "POST"])
async def fetch_medal_pr(item:IName):
    img_bytes = await ATRIproxy.format_medal_pr(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)
    
@app.api_route("/qq/medal/uu", methods=["GET", "POST"])
async def fetch_uu_medal(item:IName):
    result = await ATRIproxy.format_uu_medal(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/medal/pic", methods=["GET", "POST"])
async def fetch_special_medal(item:IName):
    img_bytes = await ATRIproxy.format_special_medal(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/png")
    else:
        return str(img_bytes)


@app.api_route("/qq/medal/download", methods=["GET", "POST"])
async def job_fetch_group_info():
    result = await ATRIproxy.format_download_medal()
    return str(result)

@app.api_route("/job/token", methods=["GET", "POST"])
def job_fetch_token():
    result = ATRIproxy.format_token()
    return str(result)

@app.api_route("/job/token/ppp", methods=["GET", "POST"])
def job_fetch_token_ppp():
    result = ATRIproxy.format_token_ppp()
    return str(result)

@app.api_route("/job/shift", methods=["GET", "POST"])
def job_shift_database():
    result = ATRIproxy.format_job_shift_database()
    return str(result)

@app.api_route("/job/updategroup", methods=["GET", "POST"])
async def job_fetch_group_info(item:ItemN):
    result = ATRIproxy.format_job_update_group_list(item.group_id, item.group_member_list)
    return str(result)

@app.api_route("/job/compress", methods=["GET", "POST"])
def job_compress_score_database():
    result = ATRIproxy.format_job_compress_score_database()
    return str(result)

@app.api_route("/job/update_info_all", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_users_info()
    return str(result)

@app.api_route("/job/update_bp_all", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_users_bp()
    return str(result)

@app.api_route("/job/update_info_bind", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_bind_users_info()
    return str(result)

@app.api_route("/job/update_bp_bind", methods=["GET", "POST"])
async def job_update_bp_all():
    result = await ATRIproxy.format_job_update_all_bind_users_bp()
    return str(result)

@app.api_route("/qq/test1", methods=["GET", "POST"])
async def fetch_test1(item:IName):
    result = await ATRIproxy.format_test1(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/test2", methods=["GET", "POST"])
async def fetch_test2(item:IName):
    result = await ATRIproxy.format_test2(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/rctpp", methods=["GET", "POST"])
async def fetch_rctpp(item:IName):
    img_bytes = await ATRIproxy.format_rctpp(item.qq_id,item.osuname,item.index)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/rctpp2", methods=["GET", "POST"])
async def fetch_rctpp2(item:IName):
    result = await ATRIproxy.format_rctpp2(item.qq_id,item.osuname,item.index)
    return str(result)

@app.api_route("/qq/skill", methods=["GET", "POST"])
async def fetch_skill(item:IName):
    result = await ATRIproxy.format_skill(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/skill/vs", methods=["GET", "POST"])
async def fetch_skill(item:IName):
    result = await ATRIproxy.format_skill_vs(item.qq_id,item.vs_qq_id,item.osuname,item.vsname)
    return str(result)

@app.api_route("/qq/bind", methods=["GET", "POST"])
async def fetch_bind(item:IName):
    result = await ATRIproxy.format_bind(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/brkup", methods=["GET", "POST"])
async def fetch_brk_up(item:IName):
    # Cache logic and cleanup moved to ATRIproxy.format_brk_up
    result = await ATRIproxy.format_brk_up(item.qq_id, item.osuname,item.beatmap_id, item.group_id)

    if result["status"] == "cached":
        return f'请求太快啦，请{result["remaining_seconds"]}s后再试试'
    elif result["status"] == "success":
        return str(result["result"])
    else:
        # Handle other potential statuses or errors from ATRIproxy
        return str(result) # Or a more specific error message

@app.api_route("/qq/brk", methods=["GET", "POST"])
async def fetch_brk(item:IName):
    img_bytes = await ATRIproxy.format_brk(item.qq_id, item.osuname,item.beatmap_id,item.group_id,item.mods_list,item.is_old)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/bd", methods=["GET", "POST"])
async def fetch_bd(item:IName):
    img_bytes = await ATRIproxy.format_bd(item.qq_id, item.osuname,item.beatmap_id,item.group_id,item.mods_list)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/update", methods=["GET", "POST"])
async def fetch_update_avatar(item:IName):
    result = await ATRIproxy.format_update_avatar(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/brk/pr", methods=["GET", "POST"])
async def jobs(item:IName):
    img_bytes = await ATRIproxy.format_brkpr(item.qq_id, item.osuname,item.group_id,item.index,item.is_old)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/pr", methods=["GET", "POST"])
async def fetch_pr(item:IName):
    img_bytes = await ATRIproxy.format_pr(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/tdba", methods=["GET", "POST"])
async def fetch_tdba(item:IName):
    img_bytes = await ATRIproxy.format_tdba(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/tdbasim", methods=["GET", "POST"])
async def fetch_tdbasim(item:IName):
    result = await ATRIproxy.format_tdba_sim(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/pttpp", methods=["GET", "POST"])
async def fetch_pttpp(item:IName):
    result = await ATRIproxy.format_pttpp(item.qq_id, item.osuname,item.pp_range)
    return str(result)

@app.api_route("/qq/addpp", methods=["GET", "POST"])
async def fetch_addpp(item:IName):
    result = await ATRIproxy.format_addpp(item.qq_id, item.osuname,item.pp_lists)
    return str(result)

@app.api_route("/whatif_backrank", methods=["GET", "POST"])
async def fetch_rank(item:ItemN):
    result = await ATRIproxy.format_calculate_rank(item.pp)
    return str(result)

@app.api_route("/whatif_backpp", methods=["GET", "POST"])
async def fetch_pp(item:ItemN):
    result = await ATRIproxy.format_calculate_pp(item.rank)
    return str(result)

@app.api_route("/qq/choke", methods=["GET", "POST"])
async def fetch_choke(item:IName):
    result = await ATRIproxy.format_choke(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/bpsim", methods=["GET", "POST"])
async def fetch_bpsim(item:IName):
    result = await ATRIproxy.format_bpsim(item.qq_id, item.osuname, item.pp_range)
    return str(result)

@app.api_route("/qq/joindate", methods=["GET", "POST"])
async def fetch_joindate(item:IName):
    result = await ATRIproxy.format_joindate(item.qq_id,item.group_id, item.osuname, item.pp_range,item.group_member_list)
    return str(result)

@app.api_route("/qq/avgstar", methods=["GET", "POST"])
async def fetch_avgstar(item:IName):
    img_bytes = await ATRIproxy.format_avgstar(item.qq_id, item.osuname,item.pp_range,item.star_min,item.star_max)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/avgpp", methods=["GET", "POST"])
async def fetch_avgpp(item:IName):
    result = await ATRIproxy.format_avgpp(item.qq_id, item.osuname, item.pp_range)
    return str(result)

@app.api_route("/qq/avgpt", methods=["GET", "POST"])
async def fetch_avgpt(item:IName):
    result = await ATRIproxy.format_avgpt(item.qq_id, item.osuname, item.pt_range)
    return str(result)

@app.api_route("/qq/avgtth", methods=["GET", "POST"])
async def fetch_avgtth(item:IName):
    result = await ATRIproxy.format_avgtth(item.qq_id, item.osuname, item.tth_range)
    return str(result)

@app.api_route("/qq/finddiff", methods=["GET", "POST"])
async def fetch_finddiff(item:ItemN):
    result = await ATRIproxy.format_finddiff(item.group_id,item.group_member_list)
    return str(result)

@app.api_route("/qq/finddiff/details", methods=["GET", "POST"])
async def fetch_finddiff_details(item:IName):
    result = await ATRIproxy.format_finddiff_details(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/activity", methods=["GET", "POST"])
async def fetch_activity(item:ItemN):
    img_bytes = await ATRIproxy.format_activity(item.group_id,item.group_member_list)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/job/update_bind_all", methods=["GET", "POST"])
async def job_update_bind_all():
    task1 = await ATRIproxy.format_job_update_all_bind_users_bp()
    # 延迟1min
    await asyncio.sleep(60)
    task2 = await ATRIproxy.format_job_update_all_bind_users_info()
    return str(task1 + task2)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008, reload=True, timeout_keep_alive=120)
