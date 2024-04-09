from Config import Config

import requests
import json



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
    def get_user_info(self,osu_name):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osu_name}?key=username'
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(url, headers=headers)

        data = response.json()
        
        return data

  
    #获取ba的bid
    def get_user_best_all_info(self,user_id):
        doucument_list=[]
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/best?mode=osu&limit=100'
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)

        data = response.json()


        count=1
        for i in data:
            id=i['user']['id']
            beatmap_id=i['beatmap']['id']
            bp_index=str(f'bp{count}_bid')
            count+=1

            doucument_list.append({'id':id,bp_index:beatmap_id})

        return doucument_list
    
    def get_user_socres_info(self,user_id,beatmap_id):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores/users/{user_id}/all?mode=osu'
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)

        data = response.json()['scores']
        
        return data
        

