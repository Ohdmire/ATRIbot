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

        self.db_bind = Mongodb('localhost', 27017, 'osu', 'bind')

        self.db_group = Mongodb('localhost', 27017, 'osu', 'group')

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

        userdata = await self.ppy.get_user_info(osuname)
        id = userdata['id']

        bps = await self.ppy.get_user_best_all_info(id)

        bpscoreid_list = []
        bpspp_list = []
        bpsbeatmapid_list = []
        # 只要成score id，其他格式化导入score表 还要pp，beatmap_id
        for bp in bps:
            scoreid = bp['id']
            scorepp = bp['pp']
            scorebeatmapid = bp['beatmap']['id']
            bpscoreid_list.append(scoreid)
            bpspp_list.append(scorepp)
            bpsbeatmapid_list.append(scorebeatmapid)

        # 更新bp的scoreid列表
        self.db_user.update(
            {"id": id},  # 查询条件
            {"$set": {'bps': bpscoreid_list, 'bps_pp': bpspp_list,
                      'bps_beatmapid': bpsbeatmapid_list}},  # 插入的数据
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

        bps_pplist = self.db_user.find_one({'id': user_id})['bps_pp']

        list1 = np.array(bps_pplist)
        list2 = np.array(self.weight_list)
        list3 = list1 * list2

        origin_pp_sum = np.sum(list3)

        return origin_pp_sum

    # 功能模块-计算pp_if_fc
    async def update_if_fc_pp(self, score_id):

        score = self.db_score.find_one({'id': score_id})

        beatmap_id = score['beatmap_id']
        mod_int = self.rosu.calculate_mod_int(score['mods'])
        acc = score['accuracy'] * 100
        # 获取osu文件来计算
        await self.rosu.get_beatmap_file_async_one(beatmap_id)
        iffcpp = await self.rosu.calculate_pp_if_fc(beatmap_id, mod_int, acc)

        self.db_score.update(
            {"id": score_id},  # 查询条件
            {"$set": {'pp_if_fc': iffcpp}},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )

    # 功能模块-计算rate
    def calculate_rate_maxcombo_factor(self, maxcombo):
        if maxcombo < 700:
            rate = 0.9
        elif maxcombo >= 700:
            rate = 0.92

        return rate

    # 功能模块-计算choke pp
    def update_choke(self, score_id, beatmap_maxcombo):

        score = self.db_score.find_one({'id': score_id})

        maxcombo = beatmap_maxcombo
        scorecombo = score['max_combo']
        rate = scorecombo / maxcombo  # rate越大，连击越多，可能越不用算choke
        standard_rate = self.calculate_rate_maxcombo_factor(maxcombo)

        if score['statistics']['count_miss'] == 0 and rate < standard_rate and rate > 0.5:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': True}},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )
        elif score['statistics']['count_miss'] == 1:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': True}},  # 插入的数据l
                upsert=True  # 如果不存在则插入
            )

        else:
            self.db_score.update(
                {"id": score_id},  # 查询条件
                {"$set": {'choke': False}},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

    # 功能模块-排序
    def sort_by_firstvalue(self, list_of_dicts):
        sorted_list = sorted(list_of_dicts, key=lambda x: list(x.values())[0])
        return sorted_list

    def sorted_by_firstvalue_reverse(self, list_of_dicts):
        sorted_list = sorted(list_of_dicts, key=lambda x: list(
            x.values())[0], reverse=True)
        return sorted_list

    def sort_by_firstkey(self, list_of_dicts):
        sorted_list = sorted(list_of_dicts, key=lambda x: list(x.keys())[0])
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
        bps_beatmapid_list = self.db_user.find_one({'id': user_id})[
            'bps_beatmapid']
        await self.rosu.get_beatmap_file_async_all(bps_beatmapid_list)

    # 数据模块-计算choke pp
    async def calculate_choke_pp(self, user_id):
        # 获取bp的scoreid
        bplists = self.db_user.find_one({'id': user_id})['bps']
        # 优化，先提前下载osu文件 方便后续update_if_fc_pp的时候不需要再去一个一个下载
        await self.get_bps_osu(user_id)
        # 判断choke
        fixed_list = []  # choke后的pp
        chokeid_list = []  # choke对应的bp id 返回字典
        total_lost_pp = 0  # 总共丢失的pp
        count = 1
        for bp in bplists:
            # 更新pp_if_fc
            await self.update_if_fc_pp(bp)  # 省了这一步的时间
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
        chokeid_list = self.sort_by_firstvalue(chokeid_list)

        choke_num = len(chokeid_list)

        return fixed_pp_sum, origin_pp_sum, total_lost_pp, chokeid_list, choke_num, weight_total_lost_pp

    # 数据模块-if刷pp
    def calculate_if_get_pp(self, user_id, pp_lists):
        # 获取bp的scoreid

        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']

        bonuspp = self.calculate_bonus_pp(user_id)

        new_pp_list = []

        bp_pp_list = self.db_user.find_one({'id': user_id})['bps_pp']

        new_pp_list = bp_pp_list.copy()

        for i in pp_lists:
            new_pp_list.append(i)

        sorted_new_pp_list = sorted(new_pp_list, reverse=True)[:100]

        list1 = np.array(sorted_new_pp_list)
        list2 = np.array(self.weight_list)
        list3 = list1 * list2

        new_pp_sum = np.sum(list3) + bonuspp

        return now_pp, new_pp_sum

    # 功能模块-更新绑定
    # 返回值：True-绑定成功 False-已经绑定
    async def update_bind(self, osuname, qq_id):
        # 先判断是否已经绑定
        bind_info = self.db_bind.find_one({'id': qq_id})
        if bind_info is not None:
            return "已经绑定过了" + bind_info['username']
        else:
            # 先获取user_id,user_name
            await self.update_user_info(osuname)
            user_id = self.db_user.find_one({'username': osuname})['id']
            user_name = self.db_user.find_one({'id': user_id})['username']
            bind_info = self.db_bind.find_one({'user_id': user_id})
            if bind_info is not None:
                return "用户" + bind_info['username'] + "已被绑定"
            if user_id is not None:  # 检查user插入的合法性
                self.db_bind.update(
                    {"id": qq_id},  # 查询条件
                    {"$set": {"id": qq_id, "username": user_name,
                              "user_id": user_id}},  # 插入的数据
                    upsert=True  # 如果不存在则插入
                )
                return f'{user_name}绑定成功'

    # 功能模块-解绑
    def delete_bind(self, qq_id):
        self.db_bind.delete({"id": qq_id})

    # 功能模块-获取绑定
    def find_bind(self, qq_id):
        bind = self.db_bind.find_one({'id': qq_id})
        return bind

    # 数据模块-gruop获取
    def update_gruop(self, group_id, member_list):

        self.db_group.update(
            {"id": group_id},  # 查询条件
            {"$set": {"id": group_id, "user_id_list": member_list}},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )

    # 数据模块-avgpp

    def calculate_avg_pp(self, user_id, pp_range):

        # 处理一下pp_range
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        start_pp = now_pp - pp_range
        end_pp = now_pp + pp_range

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        bp1_pps_list = []
        bp2_pps_list = []
        bp3_pps_list = []
        bp4_pps_list = []
        bp5_pps_list = []
        bp100_pps_list = []

        for range_user in range_users:

            try:
                bp1_pps_list.append(range_user['bps_pp'][0])
                bp2_pps_list.append(range_user['bps_pp'][1])
                bp3_pps_list.append(range_user['bps_pp'][2])
                bp4_pps_list.append(range_user['bps_pp'][3])
                bp5_pps_list.append(range_user['bps_pp'][4])
                bp100_pps_list.append(range_user['bps_pp'][99])
            except:
                try:
                    print(f'{range_user["username"]}没有bp100')
                    self.update_bplist_info(range_user['username'])
                except:
                    print(f'{range_user["username"]}没有bp100且无法更新bp100')

        # 随便找个list计数
        users_amount = len(bp1_pps_list)

        avgbp1 = np.mean(bp1_pps_list)
        avgbp2 = np.mean(bp2_pps_list)
        avgbp3 = np.mean(bp3_pps_list)
        avgbp4 = np.mean(bp4_pps_list)
        avgbp5 = np.mean(bp5_pps_list)
        avgbp100 = np.mean(bp100_pps_list)

        user_origin_bps_pp = self.db_user.find_one({'id': user_id})['bps_pp']

        user_origin_bp1 = user_origin_bps_pp[0]
        user_origin_bp2 = user_origin_bps_pp[1]
        user_origin_bp3 = user_origin_bps_pp[2]
        user_origin_bp4 = user_origin_bps_pp[3]
        user_origin_bp5 = user_origin_bps_pp[4]
        user_origin_bp100 = user_origin_bps_pp[99]

        diffbp1 = user_origin_bp1 - avgbp1
        diffbp2 = user_origin_bp2 - avgbp2
        diffbp3 = user_origin_bp3 - avgbp3
        diffbp4 = user_origin_bp4 - avgbp4
        diffbp5 = user_origin_bp5 - avgbp5
        diffbp100 = user_origin_bp100 - avgbp100

        total_diff = diffbp1 + diffbp2 + diffbp3 + diffbp4 + diffbp5

        return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pp, end_pp, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff

    # 数据模块-bp相似度寻找
    def calculate_bpsim(self, user_id, pp_range):

        # 处理一下pp_range
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        start_pp = now_pp - pp_range
        end_pp = now_pp + pp_range

        user1_bps = self.db_user.find_one({'id': user_id})['bps_beatmapid']

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        sim_list = []

        for range_user in range_users:
            try:
                user2_bps = range_user['bps_beatmapid']

                sim = len(set(user1_bps).intersection(set(user2_bps)))

                sim_list.append({range_user['username']: sim})
            except:
                try:
                    print(f'{range_user["username"]}没有bps_beatmapid')
                    self.update_bplist_info(range_user['username'])
                except:
                    print(f'{range_user["username"]}没有bps_beatmapid且无法更新bps_beatmapid')

        sorted_sim_list = self.sorted_by_firstvalue_reverse(sim_list)
        sorted_sim_list = sorted_sim_list[1:11]

        return sorted_sim_list, start_pp, end_pp

    # 数据模块-bp相似度寻找
    def calculate_bpsim_group(self, group_id, user_id, pp_range):

        # 处理一下pp_range
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        start_pp = now_pp - pp_range
        end_pp = now_pp + pp_range

        user1_bps = self.db_user.find_one({'id': user_id})['bps_beatmapid']

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        sim_list = []

        for range_user in range_users:

            # 排除掉未绑定的 取group内的
            id = range_user['id']
            qqid = self.db_bind.find_one({'user_id': id})
            if qqid is not None:
                qqid = qqid['id']
            members = self.db_group.find_one({'id': group_id})['user_id_list']
            if qqid is None or qqid not in members:
                continue

            try:
                user2_bps = range_user['bps_beatmapid']

                sim = len(set(user1_bps).intersection(set(user2_bps)))

                sim_list.append({range_user['username']: sim})
            except:
                try:
                    print(f'{range_user["username"]}没有bps_beatmapid')
                    self.update_bplist_info(range_user['username'])
                except:
                    print(f'{range_user["username"]}没有bps_beatmapid且无法更新bps_beatmapid')

        sorted_sim_list = self.sorted_by_firstvalue_reverse(sim_list)
        sorted_sim_list = sorted_sim_list[1:11]

        return sorted_sim_list, start_pp, end_pp

    # 数据模块-bp相似度vs
    def calculate_bpsim_vs(self, user_id, vsuser_id):
        user1_bps = self.db_user.find_one({'id': user_id})['bps_beatmapid']
        user2_bps = self.db_user.find_one({'id': vsuser_id})['bps_beatmapid']

        sim_list = set(user1_bps).intersection(set(user2_bps))

        user12_index_list = []

        user1_bps_pp_list = self.db_user.find_one({'id': user_id})['bps_pp']
        user2_bps_pp_list = self.db_user.find_one({'id': vsuser_id})['bps_pp']

        for i in sim_list:
            user12_index_list.append(
                {user1_bps.index(i) + 1: user2_bps.index(i) + 1})

        index_dict = self.sort_by_firstkey(user12_index_list)

        return index_dict, user1_bps_pp_list, user2_bps_pp_list
