from pymongo import MongoClient


class Mongodb:
    def __init__(self, host, port, db_name, collection_name):

        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # self.collection.create_index('userid', unique=True)

    def insert(self, data):
        self.collection.insert_one(data)

    def find(self, query):
        return self.collection.find(query)

    def find_one(self, query):
        return self.collection.find_one(query)

    def update(self, query, data, upsert=True):
        self.collection.update_one(query, data, upsert)

    def delete(self, query):
        self.collection.delete_one(query)

    def delete_all(self):
        self.collection.delete_many({})

    def count(self):
        return self.collection.count_documents({})

    def close(self):
        self.client.close()

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
