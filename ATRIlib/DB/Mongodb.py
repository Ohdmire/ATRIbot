from pymongo import MongoClient, UpdateOne


class Mongodb:
    def __init__(self, host, port, db_name, collection_name):

        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # self.collection.create_index('userid', unique=True)

    def insert(self, data):
        self.collection.insert_one(data)

    def insert_many(self, data):
        self.collection.insert_many(data)

    def find(self, query):
        return self.collection.find(query)

    def find_one(self, query):
        return self.collection.find_one(query)

    def update(self, query, data, upsert=True):
        self.collection.update_one(query, data, upsert)

    def delete(self, query):
        self.collection.delete_one(query)

    def count(self):
        return self.collection.count_documents({})

    def close(self):
        self.client.close()
        
    def aggregate(self, pipeline):
        return self.collection.aggregate(pipeline)

    def drop(self):
        self.collection.drop()

    def bulk_write(self, operations):
        return self.collection.bulk_write(operations)


db_user = Mongodb('localhost', 27017, 'osu', 'user')
db_bind = Mongodb('localhost', 27017, 'osu', 'bind')
db_score = Mongodb('localhost', 27017, 'osu', 'score')
db_bp = Mongodb('localhost', 27017, 'osu', 'bp')
db_group = Mongodb('localhost', 27017, 'osu', 'group')
db_medal = Mongodb('localhost', 27017, 'osu', 'medal')
db_solution = Mongodb('localhost', 27017, 'osu', 'solution')
db_mostplayed = Mongodb('localhost', 27017, 'osu', 'mostplayed')
db_yesterday = Mongodb('localhost', 27017, 'osu', 'yesterday')

# 写入用户信息
def update_db_user(userdata):
    db_user.update(
        {"id": userdata["id"]},  # 查询条件
        {"$set": userdata},  # 插入的数据
        upsert=True  # 如果不存在则插入
    )

# 写入到bp表
def update_db_bp(user_id,bpdata):
    db_bp.update(
        {"id": user_id},  # 查询条件
        {"$set": bpdata},  # 插入的数据
        upsert=True  # 如果不存在则不插入
    )

# 写入绑定信息
def update_db_bind(qq_id, userdata):
    db_bind.update(
        {"id": qq_id},  # 查询条件
        {"$set": {"id": qq_id, "user_id": userdata['id']}},  # 插入的数据
        upsert=True  # 如果不存在则插入
    )


# 写入用户分数
def update_db_score(scoredata):
    db_score.update(
        {"id": scoredata["id"]},  # 查询条件
        {"$set": scoredata},  # 插入的数据
        upsert=True  # 如果不存在则插入
    )

# 写入群员列表
def update_db_group(group_id,members_list):
    db_group.update(
        {"id": group_id},  # 查询条件
        {"$set": {"id": group_id, "qq_id_list": members_list}},  # 插入的数据
        upsert=True  # 如果不存在则插入
    )

# 写入游玩记录
def update_db_mostplayed(user_id,mostplayed_list):
    db_mostplayed.update(
        {"id": user_id},  # 查询条件
        {"$set": {"id": user_id, "mostplayed_list": mostplayed_list}},  # 插入的数据
        upsert=True  # 如果不存在则插入
    )

# a=MongoDB('localhost',27017,'osu','username')


# documents = [
#     {"name": "John", "age": 30, "city": "New York"},
#     {"name": "Jane", "age": 25, "city": "Chicago"},
#     {"name": "Mike", "age": 18, "city": "Los Angeles"},
#     {"name": "Anna", "age": 22, "city": "San Francisco"},
#     {"name": "Tom", "age": 32, "city": "Boston"},
# ]

# for doc in documents:
#     a.update(
#         {"name": doc["name"]},  # 查询条件
#         {"$setOnInsert": doc},  # 插入的数据
#         upsert=True  # 如果不存在则插入
#     )

# b=a.find({'name':'ATRI1024'})
# for i in b:
#     print(i)
# print(b)

def bulk_update_db_score(processed_bps):
    bulk_operations = [
        UpdateOne(
            {'id': bp['id'], 'beatmap_id': bp['beatmap_id']},
            {'$set': bp},
            upsert=True
        ) for bp in processed_bps
    ]
    db_score.bulk_write(bulk_operations)