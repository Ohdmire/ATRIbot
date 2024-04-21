
import ATRIproxy as Core


class QQ:
    def __init__(self):
        self.proxy = Core.ATRI()

    async def qq_get_user_id(self, qq_id, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_user(osuname)

    async def qq_get_bplists(self, qq_id, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_bplists(osuname)

    async def qq_get_bind(self, qq_id, osuname=None):
        await self.proxy.update_bind_qq(qq_id, osuname)

    def qq_get_group_bind(self, group_id, members_list):
        self.proxy.update_bind_group(group_id, members_list)

    async def qq_get_choke(self, qq_id, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_choke(osuname)

    async def qq_get_if_add_pp(self, qq_id, pp_list, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_if_add_pp(osuname, pp_list)

    async def qq_get_avg_pp(self, qq_id, pp_range, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_avg_pp(osuname, pp_range)

    async def qq_get_bpsim(self, qq_id, pp_range, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_bpsim(osuname, pp_range)

    async def qq_get_bpsim_group(self, group_id, qq_id, pp_range, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_bpsim_group(group_id, osuname, pp_range)

    async def qq_get_bpsimvs(self, qq_id, vs_name, osuname=None):

        if osuname is None:
            osuname = self.proxy.find_bind_name_qq(qq_id)

        return await self.proxy.get_bpsimvs(osuname, vs_name)
