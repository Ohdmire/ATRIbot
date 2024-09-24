from ATRIlib.DB.pipeline_joindate import get_joindate_group_list_from_db


def calculate_joindate(user_id,group_id, pp_range):

    result = get_joindate_group_list_from_db(user_id, group_id,pp_range)

    return result