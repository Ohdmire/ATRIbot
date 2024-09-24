from ATRIlib.DB.pipeline_bpsim import get_sim_list_from_db

def calculate_bpsim(user_id, pp_range):

    result = get_sim_list_from_db(user_id, pp_range)

    return result

    # 数据模块-bp相似度寻找