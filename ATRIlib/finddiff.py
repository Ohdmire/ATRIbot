from ATRIlib.DB.pipeline_findidff import find_differences, find_differences_details

def find_diff(group_id):
    
    raw = find_differences(group_id)

    return raw

def find_diff_details(user_id):
    
    raw = find_differences_details(user_id)

    return raw