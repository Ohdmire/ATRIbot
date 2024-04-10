from PPYapiv2 import PPYdata
from Mongodb import MongoDB

import asyncio

import json


class ATRICore:
    def __init__(self):
        self.ppy=PPYdata()
        self.ppy.get_token()

        self.db_user=MongoDB('localhost',27017,'osu','user') #数据库名字为osu，表名为user
        self.db_score=MongoDB('localhost',27017,'osu','score') #数据库名字为osu，表名为beatmap

    
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
    
    # def update_scores_info_all()


#score combo acc mods time 


a=ATRICore()

a.update_user_info('ATRI1024')

a.update_bplist_info('ATRI1024')

# b=a.db_user.find({'id':8664033})
# for i in b:
#     print(i)


a.update_scores_info("8664033","86324")