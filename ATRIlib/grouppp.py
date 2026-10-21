import statistics

from ATRIlib.DB.pipeline_grouppp import get_group_pp_list_from_db


def calculate_grouppp(group_id):

    players = get_group_pp_list_from_db(group_id)
    pp_list = [player["pp"] for player in players]

    return {
        "players": players,
        "count": len(players),
        "median": statistics.median(pp_list) if pp_list else 0,
    }
