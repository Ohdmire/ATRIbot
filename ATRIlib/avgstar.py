from ATRIlib.DB.Mongodb import db_user
import numpy as np
from ATRIlib.DB.pipeline_avgstar import get_matched_pp_list
from ATRIlib.DRAW.draw_avgstar import plot_star_pp_density

def calculate_avg_star(user_id, user_pp,pp_range,star_min,star_max):

    raw = get_matched_pp_list(user_id, pp_range,star_min,star_max)

    result = plot_star_pp_density(raw,user_pp,pp_range)

    return result

