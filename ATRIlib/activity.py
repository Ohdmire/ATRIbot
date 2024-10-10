from ATRIlib.DB.pipeline_daily import pipeline_daily_bp_data,pipeline_daily_other_data
from ATRIlib.DRAW.draw_daily import draw_daily
def get_activity(group_id):

    raw = pipeline_daily_bp_data(group_id)

    raw_other = pipeline_daily_other_data(group_id)

    img = draw_daily(raw, raw_other)

    return img