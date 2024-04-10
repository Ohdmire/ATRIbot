from PPYapiv2 import PPYdata
from Mongodb import MongoDB

import asyncio

import json

import numpy as np


class ATRICore:
    def __init__(self):
        self.ppy=PPYdata()
        self.ppy.get_token()

        self.db_user=MongoDB('localhost',27017,'osu','user') #数据库名字为osu，表名为user
        self.db_score=MongoDB('localhost',27017,'osu','score') #数据库名字为osu，表名为beatmap

        self.weight_list=[100, 95, 90.25, 85.73749999999998, 81.45062499999999, 77.37809374999998, 73.50918906249998, 69.83372960937497, 66.34204312890623, 63.02494097246091, 59.87369392383787, 56.880009227645964, 54.03600876626366, 51.33420832795048, 48.76749791155295, 46.329123015975306, 44.012666865176534, 41.812033521917705, 39.72143184582182, 37.73536025353073, 35.84859224085419, 34.05616262881148, 32.3533544973709, 30.73568677250236, 29.198902433877237, 27.738957312183377, 26.352009446574204, 25.034408974245494, 23.782688525533217, 22.593554099256554, 21.463876394293727, 20.39068257457904, 19.371148445850086, 18.402591023557584, 17.4824614723797, 16.608338398760715, 15.777921478822678, 14.989025404881545, 14.239574134637467, 13.527595427905592, 12.851215656510313, 12.208654873684797, 11.598222130000556, 11.018311023500528, 10.467395472325501, 9.944025698709225, 9.446824413773763, 8.974483193085076, 8.52575903343082, 8.09947108175928, 7.694497527671315, 7.30977265128775, 6.944284018723361, 6.597069817787194, 6.267216326897833, 5.953855510552941, 5.656162735025293, 5.3733545982740285, 5.104686868360327, 4.84945252494231, 4.606979898695195, 4.376630903760435, 4.157799358572413, 3.949909390643792, 3.752413921111602, 3.5647932250560217, 3.3865535638032207, 3.2172258856130593, 3.0563645913324065, 2.903546361765786, 2.7583690436774964, 2.6204505914936216, 2.4894280619189404, 2.3649566588229933, 2.2467088258818437, 2.134373384587751, 2.0276547153583633, 1.926271979590445, 1.829958380610923, 1.7384604615803767, 1.651537438501358, 1.5689605665762898, 1.4905125382474753, 1.4159869113351014, 1.3451875657683463, 1.2779281874799289, 1.2140317781059324, 1.1533301892006358, 1.0956636797406039, 1.0408804957535738, 0.988836470965895, 0.9393946474176, 0.8924249150467202, 0.8478036692943841, 0.8054134858296649, 0.7651428115381815, 0.7268856709612724, 0.6905413874132088, 0.6560143180425483, 0.6232136021404209]

    
    # 更新玩家信息
    def update_user_info(self,osuname):
        userdata=self.ppy.get_user_info(osuname)

        self.db_user.update(
            {"id": userdata["id"]},  # 查询条件
            {"$set": userdata},  # 插入的数据
            upsert=True  # 如果不存在则插入
            ) 
    # 更新玩家bp信息
    def update_bplist_info(self,osuname):
        #获取玩家ID
        userdata=self.ppy.get_user_info(osuname)
        id=userdata['id']
        

        bps=self.ppy.get_user_best_all_info(id)

        bpscoreid_list=[]
        #只要成score id，其他格式化导入score表
        for bp in bps:
            scoreid=bp['id']
            bpscoreid_list.append(scoreid)

        self.db_user.update(
            {"id": id},  # 查询条件
            {"$set":{'bps':bpscoreid_list}},  # 插入的数据
            upsert=True  # 如果不存在则插入
            )
        
        #格式化bp 然后导入score表
        for bp in bps:

            bp.pop("beatmap", None)
            bp.pop("user", None)
            bp.pop("beatmapset", None)
            bp.pop("weight", None)
        
        
            self.db_score.update(
                {"id": bp["id"]},  # 查询条件
                {"$set": bp},  # 插入的数据
                upsert=True  # 如果不存在则插入
                )


    def update_scores_info(self,user_id,beatmap_id):
        socresdata=self.ppy.get_user_socres_info(user_id,beatmap_id)

        for score in socresdata:
            self.db_score.update(
                {"id": score["id"]},  # 查询条件
                {"$set": score},  # 插入的数据
                upsert=True  # 如果不存在则插入
                )
            
    def calculate_origin_pp(self,user_id):
        bplist=self.db_user.find_one({'id':user_id})['bps']
        origin_pp_list=[]
        for bp in bplist:
            score=self.db_score.find_one({'id':bp})
            origin_pp=score['pp']
            origin_pp_list.append(origin_pp)
        list1=np.array(origin_pp_list)
        list2=np.array(self.weight_list)

        list3=list1*list2
        
        origin_pp_sum=np.sum(list3)

        return origin_pp_sum

    # def update_scores_info_all()


#score combo acc mods time 


a=ATRICore()

a.update_user_info('ATRI1024')

a.update_bplist_info('ATRI1024')

# b=a.db_user.find({'id':8664033})
# for i in b:
#     print(i)


# a.update_scores_info("8664033","86324")

a.calculate_origin_pp(8664033)