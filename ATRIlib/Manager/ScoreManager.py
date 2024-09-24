from ATRIlib.DB.Mongodb import db_score,update_db_score

def update_score(beatmapid,scoredata):

    scoredata.update({'beatmap_id': beatmapid}) # 加入beatmap_id

    update_db_score(scoredata)

def update_score_many(beatmapid,scoredatas):

    for scoredata in scoredatas:
        scoredata.update({'beatmap_id': beatmapid}) # 加入beatmap_id
        update_score(beatmapid,scoredata)