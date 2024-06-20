from ATRIlib.Config import Config
import requests
import aiohttp
import asyncio
import json


class PPYapiv2:
    def __init__(self):

        self.client_id = Config().osuclientid
        self.client_secret = Config().osuclientsecret
        # asyncio.run(self.jobs_refresh_token())

    async def jobs_refresh_token(self):
        while True:
            self.get_token()
            await asyncio.sleep(3600)

    # 获取访问令牌
    def get_token(self):
        url = 'https://osu.ppy.sh/oauth/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'public'
        }
        response = requests.post(url, data=data)
        self.token = response.json()['access_token']

    # 获取玩家信息id
    async def get_user_info(self, osu_name):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osu_name}/osu?key=username'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data

    # 获取玩家信息id
    async def get_user_info_fromid(self, osuid):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osuid}/osu?key=id'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data

    # 获取ba的bestall
    async def get_user_best_all_info(self, user_id):

        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/best?mode=osu&limit=100'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                # result = json.dumps(data, indent=4)
                # with open('ba.json', 'w') as f:
                #     f.write(result)
                return data

    # 获取socres
    async def get_user_socres_info(self, user_id, beatmap_id):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores/users/{user_id}/all?mode=osu'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                try:
                    data = data['scores']
                except:
                    data = []
                return data

    # 获取recent
    async def get_user_passrecent_info(self, user_id):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/recent?mode=osu'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data

    # 获取beatmap info
    async def get_beatmap_info(self, beatmap_id):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}'
        headers = {'Authorization': f'Bearer {token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data
