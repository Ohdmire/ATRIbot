import ATRIlib.Core as Core


class ATRI:
    def __init__(self):
        self.core = Core.ATRICore()

    async def get_user(self, osuname):
        data = await self.core.update_user_info(osuname)
        return data['id']

    async def get_bplists(self, osuname):
        data = await self.core.update_bplist_info(osuname)
        return data

    def find_bind_name_qq(self, qq_id):
        try:
            return self.core.find_bind(qq_id)['username']
        except:
            return None

    def find_bind_id_qq(self, qq_id):
        try:
            return self.core.find_bind(qq_id)['user_id']
        except:
            return None

    async def update_bind_qq(self, qq_id, osuname):
        return await self.core.update_bind(qq_id, osuname)

    def update_bind_group(self, group_id, members_list):
        return self.core.update_gruop(group_id, members_list)

    async def get_choke(self, osuname):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        fixed_pp_sum, origin_pp_sum, total_lost_pp, chokeid_list, choke_num, weight_total_lost_pp = await self.core.calculate_choke_pp(osuid)

        choke = ""
        count = 0
        for i in chokeid_list:
            for key, value in i.items():
                value = round(value)
                if count % 2 == 0:
                    choke += f'\nbp{key}: {value}'
                else:
                    choke += f'  bp{key}: {value}'
                count += 1

        origin_pp_sum = round(origin_pp_sum, 2)
        fixed_pp_sum = round(fixed_pp_sum, 2)
        total_lost_pp = round(total_lost_pp, 2)
        weight_total_lost_pp = round(weight_total_lost_pp, 2)

        data = f'{osuname}\'s ≤1miss choke\n总pp: {origin_pp_sum}pp({weight_total_lost_pp})\n如果不choke: {fixed_pp_sum}pp\n累加丢失的pp: {total_lost_pp}pp\n共choke:{choke_num}张\nchoke排行:{choke}'

        return data

    async def get_if_add_pp(self, osuname, pp_list):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        now_pp, new_pp_sum = self.core.calculate_if_get_pp(
            osuid, pp_list)

        now_pp = round(now_pp, 2)
        new_pp_sum = round(new_pp_sum, 2)

        diff = round(new_pp_sum - now_pp, 2)

        data = f'{osuname}\n现在的pp: {now_pp}pp\n如果加入这些pp: {new_pp_sum}pp\n增加了: {diff}pp'

        return data

    async def get_avg_pp(self, osuname, pp_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pp, end_pp, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff = self.core.calculate_avg_pp(
            osuid, pp_range)

        avgbp1 = round(avgbp1)
        avgbp2 = round(avgbp2)
        avgbp3 = round(avgbp3)
        avgbp4 = round(avgbp4)
        avgbp5 = round(avgbp5)
        avgbp100 = round(avgbp100)

        user_origin_bp1 = round(user_origin_bp1)
        user_origin_bp2 = round(user_origin_bp2)
        user_origin_bp3 = round(user_origin_bp3)
        user_origin_bp4 = round(user_origin_bp4)
        user_origin_bp5 = round(user_origin_bp5)
        user_origin_bp100 = round(user_origin_bp100)

        diffbp1 = round(diffbp1)
        diffbp2 = round(diffbp2)
        diffbp3 = round(diffbp3)
        diffbp4 = round(diffbp4)
        diffbp5 = round(diffbp5)
        diffbp100 = round(diffbp100)

        total_diff = round(total_diff)

        start_pp = round(start_pp)
        end_pp = round(end_pp)

        data = f'根据亚托莉的数据库(#{users_amount})\n{osuname}对比平均bp\n当前pp段{start_pp}pp ~ {end_pp}pp\nbp1: {user_origin_bp1}pp -- {avgbp1}pp({diffbp1})\nbp2: {user_origin_bp2}pp -- {avgbp2}pp({diffbp2})\nbp3: {user_origin_bp3}pp -- {avgbp3}pp({diffbp3})\nbp4: {user_origin_bp4}pp -- {avgbp4}pp({diffbp4})\nbp5: {user_origin_bp5}pp -- {avgbp5}pp({diffbp5})\nbp100: {user_origin_bp100}pp -- {avgbp100}pp({diffbp100})\n总计前5bp偏差:{total_diff}pp'

        return data

    async def get_avg_tth(self, osuname, tth_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_tth, end_tth, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp = self.core.calculate_avg_tth(
            osuid, tth_range)

        avgbp1 = round(avgbp1)
        avgbp2 = round(avgbp2)
        avgbp3 = round(avgbp3)
        avgbp4 = round(avgbp4)
        avgbp5 = round(avgbp5)
        avgbp100 = round(avgbp100)

        user_origin_bp1 = round(user_origin_bp1)
        user_origin_bp2 = round(user_origin_bp2)
        user_origin_bp3 = round(user_origin_bp3)
        user_origin_bp4 = round(user_origin_bp4)
        user_origin_bp5 = round(user_origin_bp5)
        user_origin_bp100 = round(user_origin_bp100)

        diffbp1 = round(diffbp1)
        diffbp2 = round(diffbp2)
        diffbp3 = round(diffbp3)
        diffbp4 = round(diffbp4)
        diffbp5 = round(diffbp5)
        diffbp100 = round(diffbp100)

        total_diff = round(total_diff)

        start_tth = round(start_tth / 10000)
        end_tth = round(end_tth / 10000)

        avgtotalpp = round(avgtotalpp, 2)
        user_now_pp = round(user_now_pp, 2)

        total_diff_total_pp = user_now_pp - avgtotalpp

        total_diff_total_pp = round(total_diff_total_pp)

        data = f'根据亚托莉的数据库(#{users_amount})\n{osuname}对比平均总打击数\n当前tth段{start_tth}w ~ {end_tth}w\npp: {user_now_pp}pp -- {avgtotalpp}pp({total_diff_total_pp})\nbp1: {user_origin_bp1}pp -- {avgbp1}pp({diffbp1})\nbp2: {user_origin_bp2}pp -- {avgbp2}pp({diffbp2})\nbp3: {user_origin_bp3}pp -- {avgbp3}pp({diffbp3})\nbp4: {user_origin_bp4}pp -- {avgbp4}pp({diffbp4})\nbp5: {user_origin_bp5}pp -- {avgbp5}pp({diffbp5})\nbp100: {user_origin_bp100}pp -- {avgbp100}pp({diffbp100})\n总计前5bp偏差:{total_diff}pp'

        return data

    async def get_avg_pt(self, osuname, pt_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        avgbp1, avgbp2, avgbp3, avgbp4, avgbp5, avgbp100, diffbp1, diffbp2, diffbp3, diffbp4, diffbp5, diffbp100, users_amount, start_pt, end_pt, user_origin_bp1, user_origin_bp2, user_origin_bp3, user_origin_bp4, user_origin_bp5, user_origin_bp100, total_diff, avgtotalpp, user_now_pp = self.core.calculate_avg_pt(
            osuid, pt_range)

        avgbp1 = round(avgbp1)
        avgbp2 = round(avgbp2)
        avgbp3 = round(avgbp3)
        avgbp4 = round(avgbp4)
        avgbp5 = round(avgbp5)
        avgbp100 = round(avgbp100)

        user_origin_bp1 = round(user_origin_bp1)
        user_origin_bp2 = round(user_origin_bp2)
        user_origin_bp3 = round(user_origin_bp3)
        user_origin_bp4 = round(user_origin_bp4)
        user_origin_bp5 = round(user_origin_bp5)
        user_origin_bp100 = round(user_origin_bp100)

        diffbp1 = round(diffbp1)
        diffbp2 = round(diffbp2)
        diffbp3 = round(diffbp3)
        diffbp4 = round(diffbp4)
        diffbp5 = round(diffbp5)
        diffbp100 = round(diffbp100)

        total_diff = round(total_diff)

        start_pt = round(start_pt / 3600)
        end_pt = round(end_pt / 3600)

        avgtotalpp = round(avgtotalpp, 2)
        user_now_pp = round(user_now_pp, 2)

        total_diff_total_pp = user_now_pp - avgtotalpp

        total_diff_total_pp = round(total_diff_total_pp)

        data = f'根据亚托莉的数据库(#{users_amount})\n{osuname}对比平均游玩时间\n当前pt段{start_pt}h ~ {end_pt}h\npp: {user_now_pp}pp -- {avgtotalpp}pp({total_diff_total_pp})\nbp1: {user_origin_bp1}pp -- {avgbp1}pp({diffbp1})\nbp2: {user_origin_bp2}pp -- {avgbp2}pp({diffbp2})\nbp3: {user_origin_bp3}pp -- {avgbp3}pp({diffbp3})\nbp4: {user_origin_bp4}pp -- {avgbp4}pp({diffbp4})\nbp5: {user_origin_bp5}pp -- {avgbp5}pp({diffbp5})\nbp100: {user_origin_bp100}pp -- {avgbp100}pp({diffbp100})\n总计前5bp偏差:{total_diff}pp'

        return data

    # async def get_avg_all(self, osuname, pp_range):

    #     osuid = await self.get_user(osuname)
    #     await self.get_bplists(osuname)

    async def get_bpsim(self, osuname, pp_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        sim_list, start_pp, end_pp = self.core.calculate_bpsim(
            osuid, pp_range)

        sim = ""

        for i in sim_list:
            for key, value in i.items():
                sim += f'\n{value}张 -> {key}'

        start_pp = round(start_pp)
        end_pp = round(end_pp)

        data = f'{osuname}的bp相似度\n当前pp段{start_pp}pp ~ {end_pp}pp{sim}'

        return data

    async def get_bpsim_group(self, group_id, osuname, pp_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        sim_list, start_pp, end_pp = self.core.calculate_bpsim_group(group_id,
                                                                     osuid, pp_range)

        sim = ""

        for i in sim_list:
            for key, value in i.items():
                sim += f'\n{key}: {value}张'

        start_pp = round(start_pp)
        end_pp = round(end_pp)

        data = f'{osuname}在本群的bp相似度\n当前pp段{start_pp}pp ~ {end_pp}pp{sim}'

        return data

    async def get_bpsimvs(self, osuname, vs_name):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        vs_osuid = await self.get_user(vs_name)
        await self.get_bplists(vs_name)

        if osuid == vs_osuid:
            return '干什么！'

        index_dict, user1_bps_pp_list, user2_bps_pp_list = self.core.calculate_bpsim_vs(
            osuid, vs_osuid)

        simvs = ""
        total_diff = 0
        amount_diff = 0

        simvs += f'{osuname} vs {vs_name}的bp对比'

        for i in index_dict:
            for key, value in i.items():
                user1_pp_value = round(user1_bps_pp_list[key - 1])
                user2_pp_value = round(user2_bps_pp_list[value - 1])
                diff = round(user1_pp_value - user2_pp_value)
                total_diff += diff
                amount_diff += 1
                if key < 10:
                    key = str(key) + "  "
                if value < 10:
                    value = str(value) + "  "

                simvs += f'\nbp{key}: {user1_pp_value}pp -- {user2_pp_value}pp ->bp{value}({diff})'
        data = f'{simvs}\n总计偏差:{total_diff}pp  共有{amount_diff}张同样的bp'

        if index_dict == []:
            data = f'{osuname}和{vs_name}没有一样的bp'
        return data

    async def get_join_date(self, group_id, osuname, pp_range):

        osuid = await self.get_user(osuname)

        calculate_join_date, index, start_pp, end_pp = self.core.calculate_join_date_group(
            group_id, osuid, pp_range)

        start_pp = round(start_pp)
        end_pp = round(end_pp)

        rank = ""

        rank += f'{osuname}注册日期在本群{index}/{len(calculate_join_date)}\n当前pp段{start_pp}pp ~ {end_pp}pp'

        count = 1
        start_count = index - 5
        end_count = index + 5

        for i in calculate_join_date:
            for key, value in i.items():
                if count >= start_count and count <= end_count:
                    rank += f'\n{value[:10]} -> {key}'
                    if count == index:
                        rank += " <- 你在这里"
                count += 1

        return rank

    async def get_group_ppmap(self, group_id, osuname, pp_range):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        sorted_count_dict, pp_dict, amount_user, start_pp, end_pp = self.core.calculate_group_ppmap(
            group_id, osuid, pp_range)

        ppmap = ''
        count = 0

        for key, value in sorted_count_dict.items():
            if count < 10:
                percent = round((value / amount_user) * 100)
                ppmap += f'\n{percent}%的人 -- m{key}'
                pp = pp_dict[key]
                pp = round(pp)
                if pp != 0:
                    ppmap += f'你已刷{pp}pp'
                count += 1
            else:
                break

        start_pp = round(start_pp)
        end_pp = round(end_pp)

        result = f'根据亚托莉的数据库(#{amount_user})\n{osuname}\n在本群的最多人刷进bp的图中\n当前pp段{start_pp}pp ~ {end_pp}pp{ppmap}'
        return result

    async def get_ptt_pp(self, osuname):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        bps_ptt_pp, now_pp = self.core.calculate_ptt_pp(osuid)

        bps_ptt_pp = round(bps_ptt_pp, 2)

        data = f'{osuname}\n现在的pp: {now_pp}pp\n预测pp: {bps_ptt_pp}pp'

        return data
    
    

    async def get_update_users(self, user_lists):
        return await self.core.update_users_async(user_lists)

    def return_all_userids(self):
        return self.core.return_all_userids()

    async def jobs_update_users(self):
        return await self.core.jobs_update_users()

    async def jobs_update_users_bps(self):
        return await self.core.jobs_update_users_bps()
