import aiohttp
# 获取谱面类型
async def get_beatmap_type(beatmap_id_list):
    url = f"http://172.17.0.1:7777/predict"
    data = {"beatmap_ids": beatmap_id_list}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            data = await response.json()
            print(data)
            return data
