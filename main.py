from fastapi import FastAPI

from pydantic import BaseModel


import ATRIhandle

import uvicorn


app = FastAPI()

atri = ATRIhandle.ATRI()


class Item(BaseModel):
    osuname: str


class Item2(BaseModel):
    osuname: str
    pp_list: list


@app.api_route("/info", methods=["GET", "POST"])
async def get_user_info(item: Item):
    result = atri.get_user(item.osuname)
    print(result)
    return result


@app.api_route("/choke", methods=["GET", "POST"])
async def get_choke_info(item: Item):
    result = await atri.get_choke(item.osuname)
    print(result)
    return result


@app.api_route("/test", methods=["GET", "POST"])
async def test():
    await atri.test()


@app.api_route("/addpp", methods=["GET", "POST"])
async def add_pp(item: Item2):
    result = await atri.get_if_add_pp(item.osuname, item.pp_list)
    print(result)
    return result

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008, reload=True)
