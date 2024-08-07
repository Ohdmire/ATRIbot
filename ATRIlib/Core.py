# from PPYapiv2 import PPYapiv2
# from Mongodb import Mongodb
# from Rosu import Rosu

from . import PPYapiv2
from .Mongodb import Mongodb
from . import Rosu
from . import Jobs
from . import Mtools
from ATRIlib.Dtools import ResultScreen, TDBA, BeatmapRankingscreeen
from ATRIlib.CommonTool import sort_by_firstkey, sort_by_firstvalue, sort_by_givenkey_reverse, sort_dict_by_value_reverse, sorted_by_firstvalue_reverse

import numpy as np
import datetime
import aiohttp


class ATRICore:
    def __init__(self):

        self.db_user = Mongodb('localhost', 27017, 'osu',
                               'user')  # 数据库名字为osu，表名为user
        # 数据库名字为osu，表名为beatmap
        self.db_score = Mongodb('localhost', 27017, 'osu', 'score')

        self.db_bind = Mongodb('localhost', 27017, 'osu', 'bind')

        self.db_group = Mongodb('localhost', 27017, 'osu', 'group')

        self.weight_list = [1.0, 0.95, 0.9025, 0.8573749999999998, 0.8145062499999999, 0.7737809374999998, 0.7350918906249998, 0.6983372960937497, 0.6634204312890623, 0.6302494097246091, 0.5987369392383787, 0.5688000922764597, 0.5403600876626367, 0.5133420832795048, 0.4876749791155295, 0.46329123015975304, 0.44012666865176536, 0.4181203352191771, 0.3972143184582182, 0.3773536025353073, 0.3584859224085419, 0.34056162628811476, 0.323533544973709, 0.3073568677250236, 0.2919890243387724, 0.27738957312183377, 0.26352009446574204, 0.2503440897424549, 0.23782688525533216, 0.22593554099256555, 0.21463876394293727, 0.2039068257457904, 0.19371148445850087, 0.18402591023557582, 0.174824614723797, 0.16608338398760714, 0.1577792147882268, 0.14989025404881545, 0.14239574134637467, 0.13527595427905592, 0.12851215656510312, 0.12208654873684796, 0.11598222130000556, 0.11018311023500528, 0.10467395472325501, 0.09944025698709226, 0.09446824413773763, 0.08974483193085075, 0.0852575903343082, 0.0809947108175928, 0.07694497527671315, 0.07309772651287749,
                            0.06944284018723361, 0.06597069817787193, 0.06267216326897833, 0.05953855510552941, 0.056561627350252934, 0.053733545982740286, 0.051046868683603266, 0.048494525249423104, 0.046069798986951946, 0.043766309037604346, 0.041577993585724136, 0.03949909390643792, 0.03752413921111602, 0.03564793225056022, 0.033865535638032206, 0.03217225885613059, 0.030563645913324066, 0.029035463617657863, 0.027583690436774964, 0.026204505914936217, 0.024894280619189402, 0.023649566588229934, 0.02246708825881844, 0.02134373384587751, 0.020276547153583634, 0.01926271979590445, 0.01829958380610923, 0.017384604615803767, 0.01651537438501358, 0.0156896056657629, 0.014905125382474753, 0.014159869113351013, 0.013451875657683464, 0.012779281874799289, 0.012140317781059324, 0.011533301892006359, 0.01095663679740604, 0.010408804957535737, 0.00988836470965895, 0.009393946474176, 0.008924249150467202, 0.00847803669294384, 0.008054134858296648, 0.007651428115381815, 0.007268856709612724, 0.006905413874132088, 0.006560143180425483, 0.006232136021404208]

        self.result = ResultScreen()
        self.ranking = BeatmapRankingscreeen()
        self.tdba = TDBA()

        print("初始化")

    # 更新token
    def update_token(self):
        PPYapiv2.token = PPYapiv2.get_token()

    # 数据模块-更新玩家信息
    async def update_user_info(self, osuname):
        userdata = await PPYapiv2.get_user_info(osuname)

        try:
            userdata["id"]
        except:
            print(userdata)
            print(PPYapiv2.token)

        self.db_user.update(
            {"id": userdata["id"]},  # 查询条件
            {"$set": userdata},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )

        self.db_bind.update(
            {"user_id": userdata['id']},  # 查询条件
            {"$set": {'username': userdata['username']}},  # 插入的数据
            upsert=False  # 不存在不插入
        )

        return userdata

    # 数据模块-更新玩家bp信息
    async def update_bplist_info(self, osuname):

        userdata = await PPYapiv2.get_user_info(osuname)
        id = userdata['id']

        bps = await PPYapiv2.get_user_best_all_info(id)

        bpscoreid_list = []
        bpspp_list = []
        bpsbeatmapid_list = []
        bpcreatedat_list = []
        # 只要成score id，其他格式化导入score表 还要pp，beatmap_id,created_at
        for bp in bps:
            scoreid = bp['id']
            scorepp = bp['pp']
            scorebeatmapid = bp['beatmap']['id']
            createdat = bp['created_at']
            bpscoreid_list.append(scoreid)
            bpspp_list.append(scorepp)
            bpsbeatmapid_list.append(scorebeatmapid)
            bpcreatedat_list.append(createdat)

        # 更新bp的scoreid列表
        self.db_user.update(
            {"id": id},  # 查询条件
            {"$set": {'bps': bpscoreid_list, 'bps_pp': bpspp_list,
                      'bps_beatmapid': bpsbeatmapid_list, 'bps_createdat': bpcreatedat_list}},  # 插入的数据
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
        socresdata = await PPYapiv2.get_user_socres_info(user_id, beatmap_id)

        for score in socresdata:
            # 加入beatmap_id
            score.update({'beatmap_id': int(beatmap_id)})

            self.db_score.update(
                {"id": score["id"]},  # 查询条件 这里的id是scoreid
                {"$set": score},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

        return socresdata

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
        mods = score['mods']
        acc = score['accuracy'] * 100
        # 获取osu文件来计算
        await Rosu.get_beatmap_file_async_one(beatmap_id, Temp=False)
        # 不需要combo计算
        ppresult = await Rosu.calculate_pp_if_all(beatmap_id, mods, acc, None, Temp=False)
        iffcpp = ppresult["fcpp"]

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
        await Rosu.get_beatmap_file_async_all(bps_beatmapid_list)

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
            ppresult = await Rosu.calculate_pp_if_all(beatmap_id, [], 0, None, Temp=False)
            maxcombo = ppresult["maxcombo"]
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
        chokeid_list = sort_by_firstvalue(chokeid_list)

        choke_num = len(chokeid_list)

        return fixed_pp_sum, origin_pp_sum, total_lost_pp, chokeid_list, choke_num, weight_total_lost_pp

    # 数据模块-if刷pp
    async def calculate_if_get_pp(self, user_id, pp_lists):
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

        # 获取变化的排名

        original_rank = self.db_user.find_one(
            {'id': user_id})['statistics']['global_rank']

        if new_pp_sum - now_pp > 1:
            try:
                new_rank = await self.get_rank_based_on_pp(new_pp_sum)
            except:
                new_rank = original_rank
            new_rank = int(new_rank)
        else:
            new_rank = original_rank

        return now_pp, new_pp_sum, original_rank, new_rank

    async def get_rank_based_on_pp(self, pp):

        url = "https://osudaily.net/data/getPPRank.php?t=pp&v=" + \
            str(pp) + "&m=0"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.text()
                return data

    async def get_rank_based_on_rank(self, rank):

        url = "https://osudaily.net/data/getPPRank.php?t=rank&v=" + \
            str(rank) + "&m=0"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.text()
                return data

    # 功能模块-更新绑定
    # 返回值：True-绑定成功 False-已经绑定
    async def update_bind(self, qq_id, osuname):
        # 先判断是否已经绑定
        bind_info = self.db_bind.find_one({'id': qq_id})
        if bind_info is not None:
            return f'你已经绑定了{bind_info["username"]} 如需解绑请联系管理员'
        else:
            # 先获取user_id,user_name
            userdata = await self.update_user_info(osuname)
            if userdata is None:
                return f'用户{osuname}不存在'
            try:
                username = userdata['username']
                user_id = self.db_user.find_one({'username': username})['id']
            except:
                return f'用户{username}不存在'
            
            user_name = self.db_user.find_one({'id': user_id})['username']
            bind_info = self.db_bind.find_one({'user_id': user_id})
            if bind_info is not None:
                return f'用户{bind_info["username"]}已被QQ({bind_info["id"]})绑定'
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

        return f'已更新群组{group_id}的成员列表'

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
                pass

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

    # 数据模块-avgtth
    def calculate_avg_tth(self, user_id, tth_range):

        # tth默认单位，w

        # 处理一下tth_range
        now_tth = self.db_user.find_one({'id': user_id})[
            'statistics']['total_hits']
        start_tth = now_tth - tth_range
        end_tth = now_tth + tth_range

        range_users = self.db_user.find(
            {'statistics.total_hits': {'$gt': start_tth, '$lt': end_tth}})

        user_now_pp = self.db_user.find_one({'id': user_id})[
            'statistics']['pp']

        bp1_pps_list = []
        bp2_pps_list = []
        bp3_pps_list = []
        bp4_pps_list = []
        bp5_pps_list = []
        bp100_pps_list = []
        total_pps_list = []

        for range_user in range_users:

            try:
                bp1_pps_list.append(range_user['bps_pp'][0])
                bp2_pps_list.append(range_user['bps_pp'][1])
                bp3_pps_list.append(range_user['bps_pp'][2])
                bp4_pps_list.append(range_user['bps_pp'][3])
                bp5_pps_list.append(range_user['bps_pp'][4])
                bp100_pps_list.append(range_user['bps_pp'][99])
                total_pps_list.append(range_user['statistics']['pp'])
            except:
                pass

        # 随便找个list计数
        users_amount = len(bp1_pps_list)

        avgbp1 = np.mean(bp1_pps_list)
        avgbp2 = np.mean(bp2_pps_list)
        avgbp3 = np.mean(bp3_pps_list)
        avgbp4 = np.mean(bp4_pps_list)
        avgbp5 = np.mean(bp5_pps_list)
        avgbp100 = np.mean(bp100_pps_list)
        avgtotalpp = np.mean(total_pps_list)

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

        return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_tth, end_tth, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp

    def calculate_avg_pt(self, user_id, pt_range):

        # pt默认单位h

        # 处理一下tth_range
        now_pt = self.db_user.find_one({'id': user_id})[
            'statistics']['play_time']
        start_pt = now_pt - pt_range
        end_pt = now_pt + pt_range

        range_users = self.db_user.find(
            {'statistics.play_time': {'$gt': start_pt, '$lt': end_pt}})

        user_now_pp = self.db_user.find_one({'id': user_id})[
            'statistics']['pp']

        bp1_pps_list = []
        bp2_pps_list = []
        bp3_pps_list = []
        bp4_pps_list = []
        bp5_pps_list = []
        bp100_pps_list = []
        total_pps_list = []

        for range_user in range_users:

            try:
                bp1_pps_list.append(range_user['bps_pp'][0])
                bp2_pps_list.append(range_user['bps_pp'][1])
                bp3_pps_list.append(range_user['bps_pp'][2])
                bp4_pps_list.append(range_user['bps_pp'][3])
                bp5_pps_list.append(range_user['bps_pp'][4])
                bp100_pps_list.append(range_user['bps_pp'][99])
                total_pps_list.append(range_user['statistics']['pp'])
            except:
                pass

        # 随便找个list计数
        users_amount = len(bp1_pps_list)

        avgbp1 = np.mean(bp1_pps_list)
        avgbp2 = np.mean(bp2_pps_list)
        avgbp3 = np.mean(bp3_pps_list)
        avgbp4 = np.mean(bp4_pps_list)
        avgbp5 = np.mean(bp5_pps_list)
        avgbp100 = np.mean(bp100_pps_list)
        avgtotalpp = np.mean(total_pps_list)

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

        return avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pt, end_pt, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp

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

            # 排除掉未绑定的
            id = range_user['id']
            qqid = self.db_bind.find_one({'user_id': id})
            if qqid is not None:
                qqid = qqid['id']
            if qqid is None:
                continue

            try:
                user2_bps = range_user['bps_beatmapid']

                sim = len(set(user1_bps).intersection(set(user2_bps)))

                sim_list.append({range_user['username']: sim})
            except:
                pass

        sorted_sim_list = sorted_by_firstvalue_reverse(sim_list)
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
                pass

        sorted_sim_list = sorted_by_firstvalue_reverse(sim_list)
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

        index_dict = sort_by_firstkey(user12_index_list)

        return index_dict, user1_bps_pp_list, user2_bps_pp_list

    # 数据模块-joindate
    def calculate_join_date_group(self, group_id, user_id, pp_range):

        # 处理一下pp_range
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        start_pp = now_pp - pp_range
        end_pp = now_pp + pp_range

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        user_joindate = self.db_user.find_one({'id': user_id})['join_date']
        osuname = self.db_user.find_one({'id': user_id})['username']

        join_date_list = []

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
                join_date_list.append(
                    {range_user['username']: range_user['join_date']})
            except:
                pass

        sorted_join_date_list = sort_by_firstvalue(
            join_date_list)

        index = sorted_join_date_list.index({osuname: user_joindate}) + 1

        return sorted_join_date_list, index, start_pp, end_pp

    def calculate_group_ppmap(self, group_id, user_id, pp_range):

        # 处理一下pp_range
        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        start_pp = now_pp - pp_range
        end_pp = now_pp + pp_range

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        count_dict = {}
        pp_dict = {}
        amount_user = 0

        user_bps_beatmapid = self.db_user.find_one({'id': user_id})[
            'bps_beatmapid']
        user_bps_pp = self.db_user.find_one({'id': user_id})['bps_pp']

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
                users_bps = range_user['bps_beatmapid']

                for i in users_bps:
                    if i in count_dict:
                        count_dict[i] += 1
                    else:
                        count_dict[i] = 1

                amount_user += 1

            except:
                pass

        # 查找已经刷过的
        for key in count_dict:
            if key in user_bps_beatmapid:
                # 查找index
                index = user_bps_beatmapid.index(key)
                scorepp = user_bps_pp[index]
                pp_dict[key] = scorepp
            else:
                pp_dict[key] = 0

        sorted_count_dict = sort_dict_by_value_reverse(count_dict)

        return sorted_count_dict, pp_dict, amount_user, start_pp, end_pp

    def calculate_ptt_pp(self, user_id):

        now_pp = self.db_user.find_one({'id': user_id})['statistics']['pp']
        # now_bp1 = self.db_user.find_one({'id': user_id})['bps_pp'][0]
        # now_bp1to2avg = sum(self.db_user.find_one(
        #     {'id': user_id})['bps_pp'][0:1]) / 2

        now_bp1 = self.db_user.find_one({'id': user_id})['bps_pp'][0]

        start_pp = now_pp - 1000
        end_pp = now_pp + 1000

        range_users = self.db_user.find(
            {'statistics.pp': {'$gt': start_pp, '$lt': end_pp}})

        # k1_bp1_list = []
        # k1_pp_list = []

        k2_bp2_list = []
        k2_pp_list = []

        for range_user in range_users:
            try:
                # k1_bp1_list.append(range_user['bps_pp'][0])
                # k1_pp_list.append(range_user['statistics']['pp'])
                # k2_bp1to2avg_list.append(sum(range_user['bps_pp'][0:1]) / 2)
                k2_bp2_list.append(range_user['bps_pp'][1])
                k2_pp_list.append(range_user['statistics']['pp'])
            except:
                pass

        # k1, b1 = Mtools.leastsquares(k1_bp1_list, k1_pp_list)

        k2, b2 = Mtools.leastsquares(k2_bp2_list, k2_pp_list)

        # avg_ptt_pp = k1 * now_bp1 + b1
        bps_ptt_pp = k2 * now_bp1 + b2

        return bps_ptt_pp, now_pp

    def calculate_tdba(self, user_id):

        osuname = self.db_user.find_one({'id': user_id})['username']

        per_time = []  # 每个时间段0-23
        sum_pp_per_hour = []  # 每个时间段的累计pp

        pp_list = self.db_user.find_one({'id': user_id})['bps_pp']
        list1 = np.array(pp_list)
        list2 = np.array(self.weight_list)
        weighted_pplist = list1 * list2
        time_list = self.db_user.find_one({'id': user_id})['bps_createdat']

        for i in range(24):
            per_time.append(i)
            sum_pp_per_hour.append(0)

        for i in range(len(weighted_pplist)):
            formated_time = datetime.datetime.strptime(
                time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            sum_pp_per_hour[hours] += weighted_pplist[i]

        # 散点图
        x_list = []
        y_list = []

        # 获取坐标
        for i in range(len(list1)):
            formated_time = datetime.datetime.strptime(
                time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            x_list.append(hours)
            y_list.append(list1[i])

        data = self.tdba.draw(sum_pp_per_hour, per_time,
                              x_list, y_list, osuname)

        return data

    def calculate_tdbavs(self, user_id, vs_id):

        osuname = self.db_user.find_one({'id': user_id})['username']
        vsname = self.db_user.find_one({'id': vs_id})['username']

        per_time = []  # 每个时间段0-23
        user1_sum_pp_per_hour = []  # 每个时间段的累计pp
        user2_sum_pp_per_hour = []

        user1_pp_list = self.db_user.find_one({'id': user_id})['bps_pp']
        user2_pp_list = self.db_user.find_one({'id': vs_id})['bps_pp']
        user1_rawpp_list = np.array(user1_pp_list)
        weight_list = np.array(self.weight_list)
        user1_weighted_pplist = user1_rawpp_list * weight_list
        user2_rawpp_list = np.array(user2_pp_list)
        user2_weighted_pplist = user2_rawpp_list * weight_list
        user1_time_list = self.db_user.find_one({'id': user_id})[
            'bps_createdat']
        user2_time_list = self.db_user.find_one({'id': vs_id})['bps_createdat']

        for i in range(24):
            per_time.append(i)
            user1_sum_pp_per_hour.append(0)
            user2_sum_pp_per_hour.append(0)

        for i in range(len(user1_weighted_pplist)):
            formated_time = datetime.datetime.strptime(
                user1_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            user1_sum_pp_per_hour[hours] += user1_weighted_pplist[i]

        for i in range(len(user2_weighted_pplist)):
            formated_time = datetime.datetime.strptime(
                user2_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            user2_sum_pp_per_hour[hours] += user2_weighted_pplist[i]

        # 散点图
        user1_x_list = []
        user1_y_list = []
        user2_x_list = []
        user2_y_list = []

        # 获取坐标
        for i in range(len(user1_rawpp_list)):
            formated_time = datetime.datetime.strptime(
                user1_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            user1_x_list.append(hours)
            user1_y_list.append(user1_rawpp_list[i])

        # 获取坐标
        for i in range(len(user2_rawpp_list)):
            formated_time = datetime.datetime.strptime(
                user2_time_list[i], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)
            hours = formated_time.hour
            user2_x_list.append(hours)
            user2_y_list.append(user2_rawpp_list[i])

        data = self.tdba.drawvs(user1_sum_pp_per_hour, user2_sum_pp_per_hour, per_time,
                                user1_x_list, user1_y_list, user2_x_list, user2_y_list, osuname, vsname)

        return data

    async def calculate_pr_score(self, user_id):
        # 计算pr分数
        data = await PPYapiv2.get_user_passrecent_info(user_id)
        data = data[0]

        if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
            # 永久保存谱面
            await Rosu.get_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

            ppresult = await Rosu.calculate_pp_if_all(
                data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=False)
        else:
            # 临时保存谱面
            await Rosu.get_beatmap_file_async_one(
                data["beatmap"]["id"], Temp=True)

            ppresult = await Rosu.calculate_pp_if_all(
                data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=True)

        result = await self.result.draw(data, ppresult)

        return result

    async def calculate_score(self, user_id, beatmap_id):

        data = await PPYapiv2.get_user_socres_info(user_id, beatmap_id)
        data = data[0]

        if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
            # 永久保存谱面
            await Rosu.get_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

            ppresult = await Rosu.calculate_pp_if_all(
                data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=False)
        else:
            # 临时保存谱面
            await Rosu.get_beatmap_file_async_one(
                data["beatmap"]["id"], Temp=True)

            ppresult = await Rosu.calculate_pp_if_all(
                data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=True)

        result = await self.result.draw(data, ppresult)

        return result

    async def calculate_beatmapranking(self, user_id, beatmap_id, group_id, mods_list=None):

        if mods_list == ['NM']:
            mods_list = []

        try:
            # 更新个人成绩

            await self.update_scores_info(user_id, beatmap_id)

            userscores = self.db_score.find(
                {"beatmap_id": beatmap_id, "user_id": user_id})

            user_best_score = {}
            user_best_score.update({"score": -1})
            for userscore in userscores:

                if userscore["score"] > user_best_score["score"]:  # 愚人节
                    if mods_list is not None:
                        try:
                            if sorted(userscore["mods"]) == sorted(mods_list):
                                user_best_score = userscore
                        except:
                            pass
                    else:
                        user_best_score = userscore

                # 加入用户名,avatar_url
            username = self.db_user.find_one(
                {"id": user_best_score["user_id"]})["username"]

            avatar_url = self.db_user.find_one(
                {"id": user_best_score["user_id"]})["avatar_url"]

            user_best_score.update({"username": username})
            user_best_score.update({"avatar_url": avatar_url})

        except:

            user_best_score = {}
            # username = self.db_user.find_one(
            #     {"id": user_id})["username"]

            user_best_score = {"user_id": user_id}

        beatmapinfo = await PPYapiv2.get_beatmap_info(beatmap_id)

        # 查找群友的最好成绩

        group_users_list = self.db_group.find_one(
            {"id": group_id})["user_id_list"]

        all_users_list = self.db_bind.find({"id": {"$in": group_users_list}})

        # 这下user_list就是本群玩家了

        other_users_best_score_list = []

        for another_user in all_users_list:

            another_userscores = self.db_score.find(
                {"beatmap_id": beatmap_id, "user_id": another_user["user_id"]})

            another_user_best_score = {}
            another_user_best_score.update({"score": -1})

            for another_userscore in another_userscores:
                if another_userscore["score"] > another_user_best_score["score"]:  # 愚人节
                    if mods_list is not None:
                        try:
                            if sorted(another_userscore["mods"]) == sorted(mods_list):
                                another_user_best_score = another_userscore
                        except:
                            pass
                    else:
                        another_user_best_score = another_userscore

            if another_user_best_score != {"score": -1}:
                other_users_best_score_list.append(another_user_best_score)

        sorted_others = sort_by_givenkey_reverse(
            other_users_best_score_list, "score")

        final_sorted_others = []

        # 加入用户名,avatar_url
        for sorted_other in sorted_others:

            try:
                username = self.db_user.find_one(
                    {"id": sorted_other["user_id"]})["username"]

                avatar_url = self.db_user.find_one(
                    {"id": sorted_other["user_id"]})["avatar_url"]

                sorted_other.update({"username": username})
                sorted_other.update({"avatar_url": avatar_url})

                final_sorted_others.append(sorted_other)
            except:
                print(f'error {sorted_other}')

        result = await self.ranking.draw(user_best_score, final_sorted_others, beatmapinfo, mods_list)

        return result

    async def calculate_beatmapranking_update(self, beatmap_id, group_id):

        beatmapinfo = await PPYapiv2.get_beatmap_info(beatmap_id)

        if beatmapinfo == {'error': "Specified beatmap difficulty couldn't be found."}:
            return "无法找到该谱面"

        # 批量获取beatmap

        # 获取user的id 遍历范围限制群友

        group_users_list = self.db_group.find_one(
            {"id": group_id})["user_id_list"]

        all_users_list = self.db_bind.find({"id": {"$in": group_users_list}})

        users_list = []

        for i in all_users_list:
            users_list.append(i["user_id"])

        # 这下user_list就是本群玩家了
        result = f'b{beatmap_id}共遍历{len(users_list)}个玩家 '
        result += await Jobs.update_users_beatmap_score_async(beatmap_id, users_list)

        return result

    async def get_interbot_test3(self, osuname):
        data = {"osuname": osuname}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://interbot.cn/osubot/test', data=data) as response:
                return await response.text()

    async def get_interbot_test4(self, osuname):
        data = {"osuname": osuname}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://interbot.cn/osubot/pptest', data=data) as response:
                return await response.text()

    def return_all_userids(self):
        users = self.db_user.find({})
        user_lists = []

        for i in users:
            user_lists.append(i['id'])

        return user_lists

    async def jobs_update_users_info(self):
        user_lists = self.return_all_userids()

        result = await Jobs.update_users_info_async(user_lists)

        return result

    async def jobs_update_users_bps(self):
        user_lists = self.return_all_userids()

        result = await Jobs.update_users_bps_async(user_lists)

        return result
