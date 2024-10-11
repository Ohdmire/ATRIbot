import aiohttp
# 获取谱面类型
async def get_beatmap_type(beatmap_id):
    url = f"http://172.17.0.1:7777/predict"
    data = {"beatmap_id": beatmap_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()