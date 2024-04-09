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
    def get_user_info(self,osuname):
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{osuname}?key=username'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)

        data = response.json()

        id=data['id']

        username=data['username']

        global_rank=data['statistics']['global_rank']
        country_rank=data['statistics']['country_rank']

        join_date=data['join_date']

        country_code=data['country']['code']

        pp=data['statistics']['pp']

        hit_accuracy=data['statistics']['hit_accuracy']

        play_count=data['statistics']['play_count']
        play_time=data['statistics']['play_time']

        ranked_score=data['statistics']['ranked_score']
        total_score=data['statistics']['total_score']

        total_hits=data['statistics']['total_hits']
        maximum_combo=data['statistics']['maximum_combo']


        ss_count=data['statistics']['grade_counts']['ss']
        s_count=data['statistics']['grade_counts']['s']
        a_count=data['statistics']['grade_counts']['a']
        ssh_count=data['statistics']['grade_counts']['ssh']
        sh_count=data['statistics']['grade_counts']['sh']

        document={'id':id,'username':username,'global_rank':global_rank,'country_rank':country_rank,'join_date':join_date,'country_code':country_code,'pp':pp,'hit_accuracy':hit_accuracy,'play_count':play_count,'play_time':play_time,'ranked_score':ranked_score,'total_score':total_score,'total_hits':total_hits,'maximum_combo':maximum_combo,'ss_count':ss_count,'s_count':s_count,'a_count':a_count,'ssh_count':ssh_count,'sh_count':sh_count}
        
        return document

  
                
    def get_user_best_all_info(self,userid):
        doucument_list=[]
        token = self.token
        url = f'https://osu.ppy.sh/api/v2/users/{userid}/scores/best?mode=osu&limit=100'
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)

        data = response.json()

        count=1
        for i in data:
            id=i['user']['id']
            username=i['user']['username']

            beatmap_id=i['beatmap']['id']

            rank=i['rank']
            perfect=i['perfect']

            score=i['score']
            combo=i['max_combo']
            acc=i['accuracy']
            mods=i['mods']
            if mods==[]:
                mods=['NM']
            time=i['created_at']

            bp_index=str(f'bp{count}')
            count+=1

            doucument_list.append({'id':id,'username':username,bp_index:{'beatmap_id':beatmap_id,'rank':rank,'perfect':perfect,'score':score,'combo':combo,'acc':acc,'mods':mods,'time':time}})

        return doucument_list
        


