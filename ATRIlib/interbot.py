import aiohttp

async def get_interbot_test1(osuname):
    data = {"osuname": osuname}
    async with aiohttp.ClientSession() as session:
        async with session.post('https://interbot.cn/osubot/test', data=data) as response:
            result_text = await response.text()
            if 'HTML' in result_text:
                raise ValueError("interbot请求错误")
            else:
                return result_text


async def get_interbot_test2(osuname):
    data = {"osuname": osuname}
    async with aiohttp.ClientSession() as session:
        async with session.post('https://interbot.cn/osubot/pptest', data=data) as response:
            result_text = await response.text()
            if 'HTML' in result_text:
                raise ValueError("interbot请求错误")
            else:
                return result_text
            
async def get_interbot_skill(osuname):
    data = {"osuname": osuname}
    async with aiohttp.ClientSession() as session:
        async with session.post('https://interbot.cn/osubot/skill', data=data) as response:
            result_text = await response.text()
            if 'HTML' in result_text:
                raise ValueError("interbot请求错误")
            else:
                return result_text