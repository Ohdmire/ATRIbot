from ATRIlib.DB.Mongodb import db_score,update_db_score,update_db_unrankscore

def update_score(beatmapid,scoredata):

    scoredata.update({'beatmap_id': beatmapid}) # 加入beatmap_id

    update_db_score(scoredata)

def update_score_many(beatmapid,scoredatas):

    for scoredata in scoredatas:
        scoredata.update({'beatmap_id': beatmapid}) # 加入beatmap_id
        update_score(beatmapid,scoredata)

def upate_unrank_score(scoredata):
    if scoredata["beatmap"]["ranked"] not in {1, 2, 4}:
        update_db_unrankscore(scoredata)