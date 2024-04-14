from fastapi import FastAPI

from pydantic import BaseModel

from typing import Optional

import ATRIhandle

import uvicorn


app = FastAPI()

atri = ATRIhandle.ATRI()


class Item(BaseModel):
    osuname: str
    qq_id: Optional[int] = None


class Item2(BaseModel):
    osuname: str
    pp_list: list
    qq_id: Optional[int] = None


class Item3(BaseModel):
    osuname: str
    pp_range: int
    qq_id: Optional[int] = None


class Item4(BaseModel):
    osuname: str
    qq_id: int


class Item5(BaseModel):
    osuname: str
    qq_id: Optional[int] = None
    vs_name: str


@app.api_route("/info", methods=["GET", "POST"])
async def get_user_info(item: Item):
    result = await atri.get_user(item.osuname)
    result2 = await atri.get_bplists(item.osuname)
    print(result, result2)
    return result, result2


@app.api_route("/choke", methods=["GET", "POST"])
async def get_choke_info(item: Item):
    result = await atri.get_choke(item.osuname, item.qq_id)
    print(result)
    return result


@app.api_route("/test", methods=["GET", "POST"])
async def test():
    await atri.test()


@app.api_route("/addpp", methods=["GET", "POST"])
async def add_pp(item: Item2):
    result = await atri.get_if_add_pp(item.osuname, item.pp_list, item.qq_id)
    print(result)
    return result


@app.api_route("/avgpp", methods=["GET", "POST"])
async def get_avg_pp(item: Item3):
    result = await atri.get_avg_pp(item.osuname, item.pp_range, item.qq_id)
    print(result)
    return result


@app.api_route("/getbind", methods=["GET", "POST"])
async def get_bind(item: Item4):
    result = await atri.get_bind(item.osuname, item.qq_id)
    print(result)
    return result


@app.api_route("/bpsim", methods=["GET", "POST"])
async def get_bpsim(item: Item3):
    result = await atri.get_bpsim(item.osuname, item.pp_range, item.qq_id)
    print(result)
    return result


@app.api_route("/bpsimvs", methods=["GET", "POST"])
async def get_bp(item: Item5):
    result = await atri.get_bpsimvs(item.osuname, item.vs_name, item.qq_id)
    print(result)
    return result

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008, reload=True)
