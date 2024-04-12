# from PPYapiv2 import PPYapiv2
# from Mongodb import Mongodb
# from Rosu import Rosu

from ATRIlib.PPYapiv2 import PPYapiv2
from ATRIlib.Mongodb import Mongodb
from ATRIlib.Rosu import Rosu

import numpy as np


class ATRICore:
    def __init__(self):
        self.ppy = PPYapiv2()
        self.ppy.get_token()

        self.rosu = Rosu()

        self.db_user = Mongodb('localhost', 27017, 'osu',
                               'user')  # 数据库名字为osu，表名为user
        # 数据库名字为osu，表名为beatmap
        self.db_score = Mongodb('localhost', 27017, 'osu', 'score')

        self.weight_list = [1.0, 0.95, 0.9025, 0.8573749999999998, 0.8145062499999999, 0.7737809374999998, 0.7350918906249998, 0.6983372960937497, 0.6634204312890623, 0.6302494097246091, 0.5987369392383787, 0.5688000922764597, 0.5403600876626367, 0.5133420832795048, 0.4876749791155295, 0.46329123015975304, 0.44012666865176536, 0.4181203352191771, 0.3972143184582182, 0.3773536025353073, 0.3584859224085419, 0.34056162628811476, 0.323533544973709, 0.3073568677250236, 0.2919890243387724, 0.27738957312183377, 0.26352009446574204, 0.2503440897424549, 0.23782688525533216, 0.22593554099256555, 0.21463876394293727, 0.2039068257457904, 0.19371148445850087, 0.18402591023557582, 0.174824614723797, 0.16608338398760714, 0.1577792147882268, 0.14989025404881545, 0.14239574134637467, 0.13527595427905592, 0.12851215656510312, 0.12208654873684796, 0.11598222130000556, 0.11018311023500528, 0.10467395472325501, 0.09944025698709226, 0.09446824413773763, 0.08974483193085075, 0.0852575903343082, 0.0809947108175928, 0.07694497527671315, 0.07309772651287749,
                            0.06944284018723361, 0.06597069817787193, 0.06267216326897833, 0.05953855510552941, 0.056561627350252934, 0.053733545982740286, 0.051046868683603266, 0.048494525249423104, 0.046069798986951946, 0.043766309037604346, 0.041577993585724136, 0.03949909390643792, 0.03752413921111602, 0.03564793225056022, 0.033865535638032206, 0.03217225885613059, 0.030563645913324066, 0.029035463617657863, 0.027583690436774964, 0.026204505914936217, 0.024894280619189402, 0.023649566588229934, 0.02246708825881844, 0.02134373384587751, 0.020276547153583634, 0.01926271979590445, 0.01829958380610923, 0.017384604615803767, 0.01651537438501358, 0.0156896056657629, 0.014905125382474753, 0.014159869113351013, 0.013451875657683464, 0.012779281874799289, 0.012140317781059324, 0.011533301892006359, 0.01095663679740604, 0.010408804957535737, 0.00988836470965895, 0.009393946474176, 0.008924249150467202, 0.00847803669294384, 0.008054134858296648, 0.007651428115381815, 0.007268856709612724, 0.006905413874132088, 0.006560143180425483, 0.006232136021404208]

    # 数据模块-更新玩家信息
    async def update_user_info(self, osuname):
        userdata = await self.ppy.get_user_info(osuname)

        self.db_user.update(
            {"id": userdata["id"]},  # 查询条件
            {"$set": userdata},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )
        return userdata

    # 数据模块-更新玩家bp信息
    async def update_bplist_info(self, osuname):
        # 获取玩家ID
        userdata = await self.ppy.get_user_info(osuname)
        id = userdata['id']

        bps = await self.ppy.get_user_best_all_info(id)

        bpscoreid_list = []
        # 只要成score id，其他格式化导入score表
        for bp in bps:
            scoreid = bp['id']
            bpscoreid_list.append(scoreid)

        self.db_user.update(
            {"id": id},  # 查询条件
            {"$set": {'bps': bpscoreid_list}},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )

        # 格式化bp 然后导入score表
        for bp in bps:

            # 加如beatmap_id
            bp.update({'beatmap_id': bp['beatmap']['id']})

            bp.pop("beatmap", None)
            bp.pop("user", None)
            bp.pop("beatmapset", None)
            bp.pop("weight", None)

            self.db_score.update(
                {"id": bp["id"]},  # 查询条件
                {"$set": bp},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

    # 数据模块-更新玩家成绩信息
    async def update_scores_info(self, user_id, beatmap_id):
        socresdata = await self.ppy.get_user_socres_info(user_id, beatmap_id)

        for score in socresdata:
            # 加入beatmap_id
            score.update({'beatmap_id': int(beatmap_id)})

            self.db_score.update(
                {"id": score["id"]},  # 查询条件 这里的id是scoreid
                {"$set": score},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

    # 功能模块-计算原始pp
    def calculate_origin_pp(self, user_id):
        bplist = self.db_user.find_one({'id': user_id})['bps']
        origin_pp_list = []
        for bp in bplist:
            score = self.db_score.find_one({'id': bp})
            origin_pp = score['pp']
            origin_pp_list.append(origin_pp)
        list1 = np.array(origin_pp_list)
        list2 = np.array(self.weight_list)

        list3 = list1 * list2

        origin_pp_sum = np.sum(list3)

        return origin_pp_sum

    # 功能模块-计算mod_int
    def calculate_mod_int(self, modlists):
        mod_int = 0
        for i in modlists:
            if i == "NF":
                mod_int += 1
            if i == "EZ":
                mod_int += 2
            if i == "TD":
                mod_int += 4
            if i == "HD":
                mod_int += 8
            if i == "HR":
                mod_int += 16
            if i == "SD":
                mod_int += 32
            if i == "DT":
                mod_int += 64
            if i == "RX":
                mod_int += 128
            if i == "HT":
                mod_int += 256
            if i == "NC":
                mod_int += 576
            if i == "FL":
                mod_int += 1024
            if i == "AT":
                mod_int += 2048
            if i == "SO":
                mod_int += 4096
            if i == "AP":
                mod_int += 8192
            if i == "PF":
                mod_int += 16416
            if i == "4K":
                mod_int += 32768
            if i == "5K":
                mod_int += 65536
            if i == "6K":
                mod_int += 131072
            if i == "7K":
                mod_int += 262144
            if i == "8K":
                mod_int += 524288
            if i == "FI":
                mod_int += 1048576
            if i == "RD":
                mod_int += 2097152
            if i == "CM":
                mod_int += 4194304
            if i == "TP":
                mod_int += 8388608
            if i == "9K":
                mod_int += 16777216
            if i == "CO":
                mod_int += 33554432
            if i == "1K":
                mod_int += 67108864
            if i == "3K":
                mod_int += 134217728
            if i == "2K":
                mod_int += 268435456
            if i == "V2":
                mod_int += 536870912
            if i == "MR":
                mod_int += 1073741824
        return mod_int

    # 功能模块-计算pp_if_fc
    async def update_if_fc_pp(self, score_id):

        score = self.db_score.find_one({'id': score_id})

        beatmap_id = score['beatmap_id']
        mod_int = self.calculate_mod_int(score['mods'])
        acc = score['accuracy'] * 100
        # 获取osu文件来计算
        await self.rosu.get_beatmap_file_async_one(beatmap_id)
        iffcpp = await self.rosu.calculate_pp_if_fc(beatmap_id, mod_int, acc)

        self.db_score.update(
            {"id": score_id},  # 查询条件
            {"$set": {'pp_if_fc': iffcpp}},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )

    # 功能模块-计算choke pp
    def update_choke(self, score_id, beatmap_maxcombo):

        score = self.db_score.find_one({'id': score_id})

        maxcombo = beatmap_maxcombo
        scorecombo = score['max_combo']
        rate = (maxcombo - scorecombo) / maxcombo

        if score['statistics']['count_miss'] == 0 and rate > 0.1:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': True}},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )
        elif score['statistics']['count_miss'] == 1:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': True}},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

        else:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': False}},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

    # 功能模块-排序
    def sort_by_firstkey(self, list_of_dicts):
        sorted_list = sorted(list_of_dicts, key=lambda x: list(x.values())[0])
        return sorted_list

    # 功能模块-计算bonus pp
    def calculate_bonus_pp(self, user_id):
        # 获取bp的scoreid
        origin_pp = self.calculate_origin_pp(user_id)
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        bonus_pp = now_pp - origin_pp
        return bonus_pp

    # 功能模块-异步批量下载bp的.osu文件
    async def get_bps_osu(self, user_id):
        bplist = self.db_user.find_one({'id': user_id})['bps']
        beatmap_id_list = []
        for bp in bplist:
            score = self.db_score.find_one({'id': bp})
            beatmap_id = score['beatmap_id']
            beatmap_id_list.append(beatmap_id)
        await self.rosu.get_beatmap_file_async_all(beatmap_id_list)

    # 数据模块-计算choke pp
    async def calculate_choke_pp(self, user_id):
        # 获取bp的scoreid
        bplists = self.db_user.find_one({'id': user_id})['bps']
        # 优化，先提前下载osu文件
        await self.get_bps_osu(user_id)
        # 判断choke
        fixed_list = []  # choke后的pp
        chokeid_list = []  # choke对应的bp id 返回字典
        total_lost_pp = 0  # 总共丢失的pp
        count = 1
        for bp in bplists:
            # 更新pp_if_fc
            await self.update_if_fc_pp(bp)
            score = self.db_score.find_one({'id': bp})
            # 更新choke
            beatmap_id = score['beatmap_id']
            maxcombo = await self.rosu.calculate_maxcombo(beatmap_id)
            self.update_choke(bp, maxcombo)
            # 重新获取score
            score = self.db_score.find_one({'id': bp})

            if score['choke']:
                fixed_list.append(score['pp_if_fc'])
                lost_pp = score['pp'] - score['pp_if_fc']
                total_lost_pp += lost_pp
                chokeid_list.append({count: lost_pp})
            else:
                fixed_list.append(score['pp'])
            count += 1
        # 按降序排列
        fixed_list.sort(reverse=True)
        # 计算pp
        list1 = np.array(fixed_list)
        list2 = np.array(self.weight_list)
        list3 = list1 * list2
        # 计算后的原始pp
        fixed_pp_origin_sum = np.sum(list3)

        bonuspp = self.calculate_bonus_pp(user_id)
        # 加上bonuspp
        fixed_pp_sum = fixed_pp_origin_sum + bonuspp
        origin_pp_sum = self.calculate_origin_pp(user_id) + bonuspp

        # 计算差值
        weight_total_lost_pp = origin_pp_sum - fixed_pp_sum
        # 按照choke程度排序
        chokeid_list = self.sort_by_firstkey(chokeid_list)

        choke_num = len(chokeid_list)

        return fixed_pp_sum, origin_pp_sum, total_lost_pp, chokeid_list, choke_num, weight_total_lost_pp
