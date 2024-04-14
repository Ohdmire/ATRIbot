import requests
import json


class PPYapiv2:
    def __init__(self):

        self.client_id = '30897'
        self.client_secret = '3P2Aztf2OJLT1YhH81h7I4WLBFfgGQwWpbNjC0zB'
        self.get_token()

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
    def get_user_info(self, osu_name):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osu_name}/osu?key=username'
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(url, headers=headers)
        data = response.json()
        return data

    # 获取ba的bid
    def get_user_best_all_info(self, user_id):

        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/best?mode=osu&limit=100'
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(url, headers=headers)
        data = response.json()
        return data


a = PPYapiv2()
b = a.get_user_info('Exrumiya')
b = json.dumps(b, indent=4)
print(b)
