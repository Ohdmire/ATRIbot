from ATRIlib.DB.Mongodb import db_beatmaptype

def update_beatmap_attributes(beatmap_id, attributes):
    valid_attributes = ['aim', 'stream', 'tech', 'alt']
    update_data = {attr: attributes.get(attr, 0) for attr in valid_attributes}
    
    # 检查是否所有属性值都为0
    if all(value == 0 for value in update_data.values()):
        # 如果所有属性值都为0，则删除该文档（如果存在）
        db_beatmaptype.delete({"id": beatmap_id})
    else:
        # 否则，更新或插入文档
        db_beatmaptype.update(
            {"id": beatmap_id},
            {"$set": update_data},
            upsert=True
        )

def get_beatmap_attributes(beatmap_id):
    result = db_beatmaptype.find_one({"id": beatmap_id})
    if result:
        return {
            "aim": result.get("aim", 0),
            "stream": result.get("stream", 0),
            "tech": result.get("tech", 0),
            "alt": result.get("alt", 0)
        }
    return None