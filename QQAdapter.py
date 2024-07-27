import ATRIproxy


async def qq_get_user_id(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    return await ATRIproxy.get_user(osuname)


async def qq_get_bplists(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    return await ATRIproxy.get_bplists(osuname)


async def qq_get_bind(qq_id, osuname=None):
    return await ATRIproxy.update_bind_qq(qq_id, osuname)


def qq_get_group_bind(group_id, members_list):
    return ATRIproxy.update_bind_group(group_id, members_list)


async def qq_get_choke(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"
    try:
        return await ATRIproxy.get_choke(osuname)
    except Exception as e:
        return f'error: {e}'


async def qq_get_if_add_pp(qq_id, pp_list, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_if_add_pp(osuname, pp_list)


async def qq_get_avg_pp(qq_id, pp_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_avg_pp(osuname, pp_range)


async def qq_get_avg_tth(qq_id, tth_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_avg_tth(osuname, tth_range)


async def qq_get_avg_pt(qq_id, pt_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_avg_pt(osuname, pt_range)


async def qq_get_bpsim(qq_id, pp_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_bpsim(osuname, pp_range)


async def qq_get_bpsim_group(group_id, qq_id, pp_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_bpsim_group(group_id, osuname, pp_range)
    except Exception as e:
        return f'error: {e}'


async def qq_get_bpsimvs(qq_id, vs_name, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_bpsimvs(osuname, vs_name)
    except Exception as e:
        return f'error: {e}'


async def qq_get_join_date(group_id, qq_id, pp_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"
    try:
        return await ATRIproxy.get_join_date(group_id, osuname, pp_range)
    except ValueError:
        return "错误 尝试输入 !getgroups更新群成员列表"
    except Exception as e:
        return f'error: {e}'


async def qq_get_group_ppmap(group_id, qq_id, pp_range, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_group_ppmap(group_id, osuname, pp_range)
    except Exception as e:
        return f'error: {e}'


async def qq_get_ptt_pp(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_ptt_pp(osuname)
    except Exception as e:
        return f'error: {e}'


async def qq_get_tdba(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_tdba(osuname)
    except Exception as e:
        return f'error: {e}'


async def qq_get_tdbavs(qq_id, vsname, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    return await ATRIproxy.get_tdbavs(osuname, vsname)


async def qq_get_pr(qq_id, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_pr(osuname)
    except Exception as e:
        return f'error: {e}'


async def qq_get_brk(qq_id, group_id, beatmap_id, mods_list, osuname=None):

    if osuname is None:
        osuname = ATRIproxy.find_bind_name_qq(qq_id)

    if osuname is None:
        return "请先绑定输入 !getbind 你的osu用户名"

    try:
        return await ATRIproxy.get_brk(osuname, group_id, beatmap_id, mods_list)
    except Exception as e:
        return f'error: {e}'


async def qq_get_brkup(beatmap_id, group_id):

    try:
        return await ATRIproxy.get_brkup(beatmap_id, group_id)
    except Exception as e:
        return f'error: {e}'
