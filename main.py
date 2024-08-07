from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import BaseModel

from typing import Optional

import ATRIproxy
import QQAdapter

import uvicorn

import os

import asyncio


class IName(BaseModel):
    qq_id: int
    osuname: Optional[str] = None


class INamePPlist(BaseModel):
    qq_id: int
    pp_list: list
    osuname: Optional[str] = None


class INamePPrange(BaseModel):
    qq_id: int
    pp_range: int
    osuname: Optional[str] = None


class IName12(BaseModel):
    qq_id: int
    vs_name: str
    osuname: Optional[str] = None


class INameQQlist(BaseModel):
    group_id: int
    members_list: list


class QQgroupPPrange(BaseModel):
    group_id: int
    qq_id: int
    pp_range: int
    osuname: Optional[str] = None


class Item7(BaseModel):
    qq_id: int
    osuname: str


class Item8(BaseModel):
    qq_id: int
    tth_range: int
    osuname: Optional[str] = None


class Item9(BaseModel):
    qq_id: int
    pt_range: int
    osuname: Optional[str] = None


class Item10(BaseModel):
    user_lists: list


class Item11(BaseModel):
    qq_id: int
    target_pp: int
    osuname: Optional[str] = None


class Item12(BaseModel):
    qq_id: int
    group_id: int
    beatmap_id: int
    mods_list: Optional[list] = None
    osuname: Optional[str] = None


class Item13(BaseModel):
    group_id: int
    beatmap_id: int


class Item14(BaseModel):
    pp: float


class Item15(BaseModel):
    rank: int


# 定时任务
def execute_periodic_update_token():
    print(f'更新token：{datetime.now()}')
    ATRIproxy.update_token()


async def execute_periodic_update_all_users():
    print(f'更新所有用户info：{datetime.now()}')
    await ATRIproxy.jobs_update_users_info()
    await asyncio.sleep(60)
    print(f'更新所有用户bps：{datetime.now()}')
    await ATRIproxy.jobs_update_users_bps()
    print(f'更新所有用户info和bps完成：{datetime.now()}')


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("init lifespan")
    scheduler.add_job(execute_periodic_update_token,
                      trigger="interval", seconds=3600)
    scheduler.add_job(execute_periodic_update_all_users,
                      trigger="cron", hour=4, minute=0)
    scheduler.start()
    yield
    print("clean up lifespan")


app = FastAPI(lifespan=app_lifespan)


@app.api_route("/token", methods=["GET", "POST"])
def update_token():
    ATRIproxy.update_token()
    return 'OK'


@app.api_route("/qq/pr", methods=["GET", "POST"])
async def get_pr(item: IName):
    result = await QQAdapter.qq_get_pr(item.qq_id, item.osuname)
    if os.path.exists('data/tmp/pr/' + result):
        return FileResponse(path='data/tmp/pr/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/brk", methods=["GET", "POST"])
async def get_brk(item: Item12):
    result = await QQAdapter.qq_get_brk(item.qq_id, item.group_id, item.beatmap_id, item.mods_list, item.osuname)
    if os.path.exists('data/tmp/brk/' + result):
        return FileResponse(path='data/tmp/brk/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/brkup", methods=["GET", "POST"])
async def get_brkup(item: Item13):
    result = await QQAdapter.qq_get_brkup(item.beatmap_id, item.group_id)
    print(result)
    return result


@app.api_route("/qq/tdba", methods=["GET", "POST"])
async def get_tdba(item: IName):
    result = await QQAdapter.qq_get_tdba(item.qq_id, item.osuname)
    if os.path.exists('data/tmp/tdba/' + result):
        return FileResponse(path='data/tmp/tdba/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/tdbavs", methods=["GET", "POST"])
async def get_tdbavs(item: IName12):
    result = await QQAdapter.qq_get_tdbavs(item.qq_id, item.vs_name, item.osuname)
    if os.path.exists('data/tmp/tdbavs/' + result):
        return FileResponse(path='data/tmp/tdbavs/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/info", methods=["GET", "POST"])
async def get_user_info(item: IName):
    result = await QQAdapter.qq_get_user_id(item.qq_id, item.osuname)
    result2 = await QQAdapter.qq_get_bplists(item.qq_id, item.osuname)
    print(result, result2)
    return result, result2


@app.api_route("/qq/choke", methods=["GET", "POST"])
async def get_choke_info(item: IName):
    result = await QQAdapter.qq_get_choke(item.qq_id, item.osuname)
    print(result)
    return result


# @app.api_route("/qq/test", methods=["GET", "POST"])
# async def test():
#     await QQAdapter.test()

@app.api_route("/qq/test3", methods=["GET", "POST"])
async def test3(item: IName):
    result = await QQAdapter.qq_get_interbot_test3(item.qq_id)
    print(result)
    return result


@app.api_route("/qq/test4", methods=["GET", "POST"])
async def test4(item: IName):
    result = await QQAdapter.qq_get_interbot_test4(item.qq_id)
    print(result)
    return result


@app.api_route("/qq/addpp", methods=["GET", "POST"])
async def add_pp(item: INamePPlist):
    result = await QQAdapter.qq_get_if_add_pp(item.qq_id, item.pp_list, item.osuname)
    print(result)
    return result


@app.api_route("/ifpp", methods=["GET", "POST"])
async def if_pp(item: Item14):
    result = await ATRIproxy.get_rank_based_pp(item.pp)
    print(result)
    return result


@app.api_route("/ifrank", methods=["GET", "POST"])
async def if_rank(item: Item15):
    result = await ATRIproxy.get_pp_based_rank(item.rank)
    print(result)
    return result


@app.api_route("/qq/avgpp", methods=["GET", "POST"])
async def get_avg_pp(item: INamePPrange):
    result = await QQAdapter.qq_get_avg_pp(item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/avgtth", methods=["GET", "POST"])
async def get_avg_tth(item: Item8):
    result = await QQAdapter.qq_get_avg_tth(item.qq_id, item.tth_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/avgpt", methods=["GET", "POST"])
async def get_avg_pt(item: Item9):
    result = await QQAdapter.qq_get_avg_pt(item.qq_id, item.pt_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/getbind", methods=["GET", "POST"])
async def get_bind(item: Item7):
    result = await QQAdapter.qq_get_bind(item.qq_id, item.osuname)
    print(result)
    return result


@app.api_route("/qq/bpsim", methods=["GET", "POST"])
async def get_bpsim(item: INamePPrange):
    result = await QQAdapter.qq_get_bpsim(item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/bpsimvs", methods=["GET", "POST"])
async def get_bp(item: IName12):
    result = await QQAdapter.qq_get_bpsimvs(item.qq_id, item.vs_name, item.osuname)
    print(result)
    return result


@app.api_route("/qq/getgroups", methods=["GET", "POST"])
def get_group_bind(item: INameQQlist):
    result = QQAdapter.qq_get_group_bind(item.group_id, item.members_list)
    print(result)
    return result


@app.api_route("/qq/bpsimgroup", methods=["GET", "POST"])
async def get_bpsim_group(item: QQgroupPPrange):
    result = await QQAdapter.qq_get_bpsim_group(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/ppmapgroup", methods=["GET", "POST"])
async def get_ppmap_group(item: QQgroupPPrange):
    result = await QQAdapter.qq_get_group_ppmap(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/joindategroup", methods=["GET", "POST"])
async def get_joindate(item: QQgroupPPrange):
    result = await QQAdapter.qq_get_join_date(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/pttpp", methods=["GET", "POST"])
async def get_ptt_pp(item: IName):
    result = await QQAdapter.qq_get_ptt_pp(item.qq_id, item.osuname)
    print(result)
    return result


# @app.api_route("/fetchusers", methods=["GET", "POST"])
# def get_all_userids():
#     result = atri_proxy.return_all_userids()
#     print(result)
#     return result


@app.api_route("/jobupdateusers", methods=["GET", "POST"])
async def job_update_users():
    result = await ATRIproxy.jobs_update_users_info()
    print(result)
    return result


@app.api_route("/jobupdateusersbps", methods=["GET", "POST"])
async def job_update_users_bps():
    result = await ATRIproxy.jobs_update_users_bps()
    print(result)
    return result


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008, reload=True)
