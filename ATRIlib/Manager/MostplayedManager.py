from ATRIlib.DB.Mongodb import update_db_mostplayed

def update_mostplayed(user_id,mostplayed_list):
    update_db_mostplayed(user_id,mostplayed_list)