from ATRIlib.DB.Mongodb import db_beatmaptype

def update_beatmap_attributes(beatmap_id, attributes):
    beatmap_id = int(beatmap_id)
    valid_attributes = ['aim', 'stream', 'tech', 'alt']
    update_data = {}
    
    for attr in valid_attributes:
        if attr in attributes:
            value = attributes[attr]
            if isinstance(value, (int, float)) and value != 0:
                update_data[attr] = value
    
    if not update_data:
        # 如果没有有效的非零属性值，则删除该文档（如果存在）
        db_beatmaptype.delete({"id": beatmap_id})
    else:
        # 否则，更新或插入文档
        db_beatmaptype.update(
            {"id": beatmap_id},
            {"$set": update_data},
            upsert=True
        )