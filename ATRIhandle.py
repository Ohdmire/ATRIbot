
import ATRIlib.Core as Core


class ATRI:
    def __init__(self):
        self.core = Core.ATRICore()

    async def get_user(self, osuname):
        data = await self.core.update_user_info(osuname)
        return data['id']

    async def get_bplists(self, osuname):
        status = await self.core.update_bplist_info(osuname)
        if status:
            return f'update {osuname} bplist success'

    async def get_choke(self, osuname):

        try:

            osuid = await self.get_user(osuname)
            await self.get_bplists(osuname)

            fixed_pp_sum, origin_pp_sum, total_lost_pp, chokeid_list, choke_num, weight_total_lost_pp = await self.core.calculate_choke_pp(osuid)

            choke = ""
            count = 0
            for i in chokeid_list:
                for key, value in i.items():
                    value = round(value, 2)
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

    async def get_if_add_pp(self, osuname, pp_list):

        osuid = await self.get_user(osuname)
        await self.get_bplists(osuname)

        now_pp, new_pp_sum = self.core.calculate_if_get_pp(
            osuid, pp_list)

        now_pp = round(now_pp, 2)
        new_pp_sum = round(new_pp_sum, 2)

        diff = round(new_pp_sum - now_pp, 2)

        data = f'{osuname}现在的pp: {now_pp}pp\n如果加入这些pp: {new_pp_sum}pp\n增加了: {diff}pp'

        return data
