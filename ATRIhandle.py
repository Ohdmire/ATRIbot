
import ATRIlib.Core as Core


class ATRI:
    def __init__(self):
        self.core = Core.ATRICore()

    async def get_user(self, osuname,):
        data = await self.core.update_user_info(osuname)
        return data['id']

    async def get_bplists(self, osuname):
        data = await self.core.update_bplist_info(osuname)
        return data

    async def get_bind(self, osuname, qq_id):
        try:
            data = await self.core.update_bind(osuname, qq_id)
            await self.core.update_bplist_info(osuname)
            return data
        except Exception as e:
            return f'error: {e}'

    async def get_choke(self, osuname, qq_id=None):

        try:
            try:
                osuname = self.core.get_bind(qq_id)['username']
            except:
                pass
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

            data = f'{osuname}\'s choke\n总pp: {origin_pp_sum}pp({weight_total_lost_pp})\n如果不choke: {fixed_pp_sum}pp\n累加丢失的pp: {total_lost_pp}pp\n共choke:{choke_num}张\nchoke排行:{choke}'

            return data

        except Exception as e:
            return f'error: {e}'

    async def get_if_add_pp(self, osuname, pp_list, qq_id=None):

        try:
            osuname = self.core.get_bind(qq_id)['username']
        except:
            pass
        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        now_pp, new_pp_sum = self.core.calculate_if_get_pp(
            osuid, pp_list)

        now_pp = round(now_pp, 2)
        new_pp_sum = round(new_pp_sum, 2)

        diff = round(new_pp_sum - now_pp, 2)

        data = f'{osuname}现在的pp: {now_pp}pp\n如果加入这些pp: {new_pp_sum}pp\n增加了: {diff}pp'

        return data

    async def get_avg_pp(self, osuname, pp_range, qq_id=None):

        try:

            osuname = self.core.get_bind(qq_id)['username']
        except:
            pass
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

        start_pp = round(start_pp, 2)
        end_pp = round(end_pp, 2)

        data = f'根据亚托莉的数据库(#{users_amount})\n当前pp段{start_pp} ~ {end_pp}\nbp1: {user_origin_bp1}pp -- {avgbp1}pp({diffbp1})\nbp2: {user_origin_bp2}pp -- {avgbp2}pp({diffbp2})\nbp3: {user_origin_bp3}pp -- {avgbp3}pp({diffbp3})\nbp4: {user_origin_bp4}pp -- {avgbp4}pp({diffbp4})\nbp5: {user_origin_bp5}pp -- {avgbp5}pp({diffbp5})\nbp100: {user_origin_bp100}pp -- {avgbp100}pp({diffbp100})\n总计前5bp偏差:{total_diff}pp'

        return data

    async def get_bpsim(self, osuname, pp_range, qq_id=None):

        try:

            try:
                osuname = self.core.get_bind(qq_id)['username']
            except:
                pass
            osuid = await self.get_user(osuname)
            await self.get_bplists(osuname)

            sim_list, start_pp, end_pp = self.core.calculate_bpsim(osuid, pp_range)

            sim = ""

            for i in sim_list:
                for key, value in i.items():
                    sim += f'\n{key}: {value}张'

            start_pp = round(start_pp, 2)
            end_pp = round(end_pp, 2)

            data = f'{osuname}的bp相似度\n当前pp段{start_pp} ~ {end_pp}{sim}'

            return data
        
        except Exception as e:
            return f'error: {e}'

    async def get_bpsimvs(self, osuname, vs_name, qq_id=None):

        try:

            try:
                osuname = self.core.get_bind(qq_id)['username']
            except:
                pass
            osuid = await self.get_user(osuname)
            await self.get_bplists(osuname)

            vs_osuid = await self.get_user(vs_name)
            await self.get_bplists(vs_name)

            index_dict, user1_bps_pp_list, user2_bps_pp_list = self.core.calculate_bpsim_vs(
                osuid, vs_osuid)

            simvs = ""
            total_diff = 0

            simvs += f'{osuname} vs {vs_name}的bp对比'

            for i in index_dict:
                for key, value in i.items():
                    user1_pp_value = round(user1_bps_pp_list[key - 1])
                    user2_pp_value = round(user2_bps_pp_list[value - 1])
                    diff = round(user1_pp_value - user2_pp_value)
                    total_diff += diff
                    simvs += f'\nbp{key}: {user1_pp_value}pp -- {user2_pp_value}pp ->bp{value}({diff})'
            data = f'{simvs}\n总计偏差:{total_diff}pp'
            return data
        
        except Exception as e:
            return f'error: {e}'
