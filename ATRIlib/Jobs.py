import asyncio
from ATRIlib.Mongodb import Mongodb
import time


class Jobs:

    def __init__(self, PPY):
        self.ppy = PPY

        self.db_user = Mongodb('localhost', 27017, 'osu', 'user')
        self.db_score = Mongodb('localhost', 27017, 'osu', 'score')

    async def update_user(self, osuid, seamaphore):

        async with seamaphore:
            try:
                userdata = await self.ppy.get_user_info_fromid(osuid)
            except:
                return None

        try:
            userdata["id"]
        except:
            return None

        self.db_user.update(
            {"id": userdata["id"]},  # 查询条件
            {"$set": userdata},  # 插入的数据
            upsert=True  # 如果不存在则插入
        )
        return userdata['id']

    async def update_user_bps(self, osuid, seamaphore):

        id = osuid

        async with seamaphore:
            try:
                bps = await self.ppy.get_user_best_all_info(id)
            except:
                return None

        bpscoreid_list = []
        bpspp_list = []
        bpsbeatmapid_list = []
        # 只要成score id，其他格式化导入score表 还要pp，beatmap_id
        for bp in bps:
            try:
                scoreid = bp['id']
            except:
                return None
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

    async def update_users_scores(self, beatmap_id, osuid, semaphore):

        id = osuid

        async with semaphore:
            socresdata = await self.ppy.get_user_socres_info(id, beatmap_id)

        for score in socresdata:
            # 加入beatmap_id
            score.update({'beatmap_id': int(beatmap_id)})

            self.db_score.update(
                {"id": score["id"]},  # 查询条件
                {"$set": score},  # 插入的数据
                upsert=True  # 如果不存在则插入
            )

    async def update_users_info_async(self, users_lists):
        total_users = len(users_lists)

        start_time = time.time()

        semaphore = asyncio.Semaphore(100)
        tasks = [self.update_user(user, semaphore) for user in users_lists]
        result = await asyncio.gather(*tasks)

        end_time = time.time()

        total_time = end_time - start_time
        total_time = round(total_time, 2)

        try:
            result.remove(None)
        except:
            pass

        success_users = len(result)

        count = success_users / total_users

        return f'成功率{count} 用时{total_time}s'

    async def update_users_bps_async(self, users_lists):
        total_users = len(users_lists)

        start_time = time.time()

        semaphore = asyncio.Semaphore(100)
        tasks = [self.update_user_bps(user, semaphore) for user in users_lists]
        result = await asyncio.gather(*tasks)

        end_time = time.time()

        total_time = end_time - start_time
        total_time = round(total_time, 2)

        try:
            result.remove(None)
        except:
            pass

        success_users = len(result)

        count = success_users / total_users

        return f'成功率{count} 用时{total_time}s'

    async def update_users_beatmap_score_async(self, beatmap_id, users_lists):

        total_users = len(users_lists)

        start_time = time.time()

        semaphore = asyncio.Semaphore(100)

        tasks = [self.update_users_scores(
            beatmap_id, user, semaphore) for user in users_lists]

        result = await asyncio.gather(*tasks)

        endtime = time.time()

        total_time = endtime - start_time
        total_time = round(total_time, 2)

        try:
            result.remove(None)
        except:
            pass

        success_users = len(result)

        count = success_users / total_users

        return f'成功率{count*100:.2f}% 用时{total_time}s'
