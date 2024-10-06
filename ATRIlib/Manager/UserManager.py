from ATRIlib.DB.Mongodb import update_db_user, update_db_bind, bulk_update_db_score, update_db_bp

# 更新用户信息
def update_user(userdata):

    update_db_user(userdata)

# 更新绑定信息
def update_bind(qq_id, userdata):

    update_db_bind(qq_id, userdata)


# 更新用户bp
def update_bp(bpdatas):
    user_id = bpdatas[0]['user']['id']

    # 使用列表推导式构建数据
    processed_bps = [{
        'id': user_id,
        'beatmap_id': bp['beatmap']['id'],
        'pp': bp['pp'],
        'created_at': bp['created_at'],
        'statistics': bp['statistics'],
        'max_combo': bp['max_combo'],
        'accuracy': bp['accuracy'],
        'mods': bp['mods'],
        **{k: v for k, v in bp.items() if k not in ['beatmap', 'user', 'beatmapset', 'weight']}
    } for bp in bpdatas]

    # 构建最终的 BP 数据
    final_bp_data = {
        'bps': [bp['id'] for bp in bpdatas],
        'bps_pp': [bp['pp'] for bp in bpdatas],
        'bps_beatmapid': [bp['beatmap']['id'] for bp in bpdatas],
        'bps_createdate': [bp['created_at'] for bp in bpdatas],
        'bps_statistics': [bp['statistics'] for bp in bpdatas],
        'bps_maxcombo': [bp['max_combo'] for bp in bpdatas],
        'bps_acc': [bp['accuracy'] for bp in bpdatas],
        'bps_mods': [bp['mods'] for bp in bpdatas]
    }

    # 批量更新 score 表
    bulk_update_db_score(processed_bps)

    # 更新 user 表中的 BP 数据
    update_db_bp(user_id, final_bp_data)

    return final_bp_data