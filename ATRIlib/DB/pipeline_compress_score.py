from ATRIlib.DB.Mongodb import db_score


def remove_non_max_score_docs():
    pipeline = [
        {
            '$group': {
                '_id': {
                    'user_id': '$user_id',
                    'mods': '$mods',
                    'beatmap_id': '$beatmap_id'
                },
                'maxScore': {'$max': '$score'},
                'docs': {'$push': '$$ROOT'}
            }
        },
        {
            '$unwind': '$docs'
        },
        {
            '$match': {
                '$expr': {
                    '$lt': ['$docs.score', '$maxScore']
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'user_id': '$docs.user_id',
                'mods': '$docs.mods',
                'beatmap_id': '$docs.beatmap_id',
                'score': '$docs.score'
            }
        }
    ]

    # 执行聚合查询
    results = list(db_score.aggregate(pipeline))

    for result in results:
        db_score.delete(result)

    count = len(results)

    return count


