from ATRIlib.DB.Mongodb import update_db_user, update_db_bind, bulk_update_db_score, update_db_bp
from ATRIlib.DB.Mongodb import db_score,db_bp
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
        'ended_at': bp['ended_at'],
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
        'bps_createdate': [bp['ended_at'] for bp in bpdatas],
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

def get_bp_score_struct(user_id,index):
    bpstruct = db_bp.find_one({'id': user_id})
    bps_scoreids = bpstruct['bps']
    score_id = bps_scoreids[index]

    score_struct = db_score.find_one({'id': score_id})

    if "great" not in score_struct["statistics"]:
        score_struct["statistics"]["great"] = 0
    if "ok" not in score_struct["statistics"]:
        score_struct["statistics"]["ok"] = 0
    if "meh" not in score_struct["statistics"]:
        score_struct["statistics"]["meh"] = 0
    if "miss" not in score_struct["statistics"]:
        score_struct["statistics"]["miss"] = 0

    return score_struct