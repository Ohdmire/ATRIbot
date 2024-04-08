from Config import Config

import requests



class PPYdata:
    def __init__(self):

        self.client_id = Config().osuclientid
        self.client_secret = Config().osuclientsecret

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
    def get_user_id(self,osuname):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osuname}?key=username'
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)
        return response.json()
  
                


        

    