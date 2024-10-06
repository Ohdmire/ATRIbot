from ATRIlib.DB.pipeline_findidff import find_differences

def find_diff(group_id):
    
    raw = find_differences(group_id)

    return raw