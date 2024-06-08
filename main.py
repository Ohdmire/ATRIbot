from fastapi import FastAPI
from fastapi.responses import FileResponse

from pydantic import BaseModel

from typing import Optional

import QQAdapter
import ATRIproxy

import uvicorn

import os


app = FastAPI()

atri_qq = QQAdapter.QQ()
atri_proxy = ATRIproxy.ATRI()


class Item(BaseModel):
    qq_id: int
    osuname: Optional[str] = None


class Item2(BaseModel):
    qq_id: int
    pp_list: list
    osuname: Optional[str] = None


class Item3(BaseModel):
    qq_id: int
    pp_range: int
    osuname: Optional[str] = None


class Item4(BaseModel):
    qq_id: int
    vs_name: str
    osuname: Optional[str] = None


class Item5(BaseModel):
    group_id: int
    members_list: list


class Item6(BaseModel):
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


@app.api_route("/qq/pr", methods=["GET", "POST"])
async def get_pr(item: Item):
    result = await atri_qq.qq_get_pr(item.qq_id, item.osuname)
    if os.path.exists('data/tmp/pr/' + result):
        return FileResponse(path='data/tmp/pr/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/brk", methods=["GET", "POST"])
async def get_brk(item: Item12):
    result = await atri_qq.qq_get_brk(item.qq_id, item.group_id, item.beatmap_id, item.mods_list, item.osuname)
    if os.path.exists('data/tmp/brk/' + result):
        return FileResponse(path='data/tmp/brk/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/brkup", methods=["GET", "POST"])
async def get_brkup(item: Item13):
    result = await atri_qq.qq_get_brkup(item.beatmap_id, item.group_id)
    print(result)
    return result


@app.api_route("/qq/tdba", methods=["GET", "POST"])
async def get_tdba(item: Item):
    result = await atri_qq.qq_get_tdba(item.qq_id, item.osuname)
    if os.path.exists('data/tmp/tdba/' + result):
        return FileResponse(path='data/tmp/tdba/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/tdbavs", methods=["GET", "POST"])
async def get_tdbavs(item: Item4):
    result = await atri_qq.qq_get_tdbavs(item.qq_id, item.vs_name, item.osuname)
    if os.path.exists('data/tmp/tdbavs/' + result):
        return FileResponse(path='data/tmp/tdbavs/' + result)
    else:
        print('File not found')
        return result


@app.api_route("/qq/info", methods=["GET", "POST"])
async def get_user_info(item: Item):
    result = await atri_qq.qq_get_user_id(item.qq_id, item.osuname)
    result2 = await atri_qq.qq_get_bplists(item.qq_id, item.osuname)
    print(result, result2)
    return result, result2


@app.api_route("/qq/choke", methods=["GET", "POST"])
async def get_choke_info(item: Item):
    result = await atri_qq.qq_get_choke(item.qq_id, item.osuname)
    print(result)
    return result


# @app.api_route("/qq/test", methods=["GET", "POST"])
# async def test():
#     await atri_qq.test()


@app.api_route("/qq/addpp", methods=["GET", "POST"])
async def add_pp(item: Item2):
    result = await atri_qq.qq_get_if_add_pp(item.qq_id, item.pp_list, item.osuname)
    print(result)
    return result


@app.api_route("/qq/avgpp", methods=["GET", "POST"])
async def get_avg_pp(item: Item3):
    result = await atri_qq.qq_get_avg_pp(item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/avgtth", methods=["GET", "POST"])
async def get_avg_tth(item: Item8):
    result = await atri_qq.qq_get_avg_tth(item.qq_id, item.tth_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/avgpt", methods=["GET", "POST"])
async def get_avg_pt(item: Item9):
    result = await atri_qq.qq_get_avg_pt(item.qq_id, item.pt_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/getbind", methods=["GET", "POST"])
async def get_bind(item: Item7):
    result = await atri_qq.qq_get_bind(item.qq_id, item.osuname)
    print(result)
    return result


@app.api_route("/qq/bpsim", methods=["GET", "POST"])
async def get_bpsim(item: Item3):
    result = await atri_qq.qq_get_bpsim(item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/bpsimvs", methods=["GET", "POST"])
async def get_bp(item: Item4):
    result = await atri_qq.qq_get_bpsimvs(item.qq_id, item.vs_name, item.osuname)
    print(result)
    return result


@app.api_route("/qq/getgroups", methods=["GET", "POST"])
def get_group_bind(item: Item5):
    result = atri_qq.qq_get_group_bind(item.group_id, item.members_list)
    print(result)
    return result


@app.api_route("/qq/bpsimgroup", methods=["GET", "POST"])
async def get_bpsim_group(item: Item6):
    result = await atri_qq.qq_get_bpsim_group(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/ppmapgroup", methods=["GET", "POST"])
async def get_ppmap_group(item: Item6):
    result = await atri_qq.qq_get_group_ppmap(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/joindategroup", methods=["GET", "POST"])
async def get_joindate(item: Item6):
    result = await atri_qq.qq_get_join_date(
        item.group_id, item.qq_id, item.pp_range, item.osuname)
    print(result)
    return result


@app.api_route("/qq/pttpp", methods=["GET", "POST"])
async def get_ptt_pp(item: Item):
    result = await atri_qq.qq_get_ptt_pp(item.qq_id, item.osuname)
    print(result)
    return result


@app.api_route("/updateusers", methods=["GET", "POST"])
async def get_updateusers(item: Item10):
    result = await atri_proxy.get_update_users(item.user_lists)
    print(result)
    return result


@app.api_route("/fetchusers", methods=["GET", "POST"])
def get_all_userids():
    result = atri_proxy.return_all_userids()
    print(result)
    return result


@app.api_route("/jobupdateusers", methods=["GET", "POST"])
async def job_update_users():
    result = await atri_proxy.jobs_update_users()
    print(result)
    return result


@app.api_route("/jobupdateusersbps", methods=["GET", "POST"])
async def job_update_users_bps():
    result = await atri_proxy.jobs_update_users_bps()
    print(result)
    return result


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008, reload=True)
