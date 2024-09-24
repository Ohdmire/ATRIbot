from ATRIlib.DB.Mongodb import update_db_user, update_db_bind, update_db_score,update_db_bp

# 更新用户信息
def update_user(userdata):

    update_db_user(userdata)

# 更新绑定信息
def update_bind(qq_id, userdata):

    update_db_bind(qq_id, userdata)


# 更新用户bp
def update_bp(bpdatas):
    bpscoreid_list = []
    bpspp_list = []
    bpsbeatmapid_list = []
    bpscreatedate_list = []
    bpsstatistics_list = []
    bpsmaxcombo_list = []
    bpsacc_list = []
    bpsmods_list = []
    user_id = bpdatas[0]['user']['id']

        # 格式化bp 然后导入score表 同时获取一个特别的列表 导入user表便于查询
    for bpdata in bpdatas:

        beatmapid = bpdata['beatmap']['id']
        scoreid = bpdata['id']
        scorepp = bpdata['pp']
        scorebeatmapid = bpdata['beatmap']['id']
        createdate = bpdata['created_at']
        statistics = bpdata['statistics']
        maxcombo = bpdata['max_combo']
        acc = bpdata['accuracy']
        mods = bpdata['mods']
        bpscoreid_list.append(scoreid)
        bpspp_list.append(scorepp)
        bpsbeatmapid_list.append(scorebeatmapid)
        bpscreatedate_list.append(createdate)
        bpsstatistics_list.append(statistics)
        bpsmaxcombo_list.append(maxcombo)
        bpsacc_list.append(acc)
        bpsmods_list.append(mods)

        # 加上beatmap_id,id去除...
        bpdata.update({'id': user_id})
        bpdata.update({'beatmap_id': beatmapid})

        bpdata.pop("beatmap", None)
        bpdata.pop("user", None)
        bpdata.pop("beatmapset", None)
        bpdata.pop("weight", None)

        update_db_score(bpdata)

    final_bp_data = {'bps': bpscoreid_list, 'bps_pp': bpspp_list,
                  'bps_beatmapid': bpsbeatmapid_list, 'bps_createdate': bpscreatedate_list ,
                     'bps_statistics':bpsstatistics_list, 'bps_maxcombo': bpsmaxcombo_list,
                     'bps_acc':bpsacc_list, 'bps_mods':bpsmods_list}

    update_db_bp(user_id,final_bp_data)

    return final_bp_data