import aiohttp
from aiohttp import ClientTimeout
import asyncio

async def get_beatmap_type(beatmap_id):
    url = "http://172.17.0.1:7777/predict"
    data = {"beatmap_ids": [beatmap_id]}

    # 设置总超时为 10 秒
    timeout = ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise ValueError(f"请求失败，状态码: {response.status}")
                data = await response.json()
                print(data)
                return data
    except asyncio.TimeoutError:
        print("请求超时，强制中断")
        raise TimeoutError("请求超过 10 秒未响应，已取消")
    except aiohttp.ClientError as e:
        print(f"请求发生错误: {str(e)}")
        raise