import requests
import aiohttp

from ATRIlib.config import osuclientid, osuclientsecret

client_id = osuclientid
client_secret = osuclientsecret

# 获取访问令牌
token = None

def get_token():
    global token
    url = 'https://osu.ppy.sh/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    response = requests.post(url, data=data)
    token = response.json()['access_token']

get_token()


# 获取玩家信息id
async def get_user_info(osuname):
    url = f'https://osu.ppy.sh/api/v2/users/{osuname}/osu?key=username'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data


# 获取玩家信息id
async def get_user_info_fromid(osuid):

    url = f'https://osu.ppy.sh/api/v2/users/{osuid}/osu?key=id'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data


# 获取ba的bestall
async def get_user_best_all_info(user_id):
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
async def get_user_scores_info(user_id, beatmap_id):
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
async def get_user_passrecent_info(user_id):
    url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/recent?mode=osu'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data


# 获取beatmap info
async def get_beatmap_info(beatmap_id):
    url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}'
    headers = {'Authorization': f'Bearer {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data
