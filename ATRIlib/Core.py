from ATRIlib.PPYapiv2 import PPYdata
from ATRIlib.Mongodb import MongoDB

import asyncio

import json


class ATRICore:
    def __init__(self):
        self.ppy=PPYdata()
        self.ppy.get_token()

        self.db_user=MongoDB('localhost',27017,'osu','user') #数据库名字为osu，表名为user
        self.db_beatmap=MongoDB('localhost',27017,'osu','beatmap') #数据库名字为osu，表名为beatmap

    
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
        userdata=self.ppy.get_user_info(osuname)

        userid=userdata['id']
        data=self.ppy.get_user_best_all_info(userid)

        for i in data:
            self.db_user.update(
                {"id": i["id"]},  # 查询条件
                {"$set": i},  # 插入的数据
                upsert=True  # 如果不存在则插入
                )
    

#score combo acc mods time 




a=ATRICore()

a.update_user_info('ATRI1024')


a.update_bplist_info('ATRI1024')
b=a.db_user.find({'username':'ATRI1024'})
for i in b:
    print(i)