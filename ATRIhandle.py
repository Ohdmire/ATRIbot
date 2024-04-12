
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

            for i in chokeid_list:
                for key, value in i.items():
                    value = round(value, 2)
                    choke += f'\nbp{key}: {value}'

            origin_pp_sum = round(origin_pp_sum, 2)
            fixed_pp_sum = round(fixed_pp_sum, 2)
            total_lost_pp = round(total_lost_pp, 2)
            weight_total_lost_pp = round(weight_total_lost_pp, 2)

            data = f'{osuname}\'s choke\n总pp: {origin_pp_sum}pp({weight_total_lost_pp})\n如果不choke: {fixed_pp_sum}pp\n累加丢失的pp: {total_lost_pp}pp\n共choke:{choke_num}张\nchoke排行:{choke}'

            return data

        except Exception as e:
            return f'error: {e}'

    async def test(self):
        await self.get_user('ATRI1024')
        await self.get_bplists('ATRI1024')
        await self.core.get_bps_osu(user_id=8664033)
