# 导出db里面的user表
import requests
import json
import asyncio
import aiohttp
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


m = Mongodb('localhost', 27017, 'osu', 'user')

user_list = []

b = m.find({})
for i in b:
    user_name = i['username']
    user_list.append(user_name)


# 保存json
with open('user_list.json', 'w') as f:
    json.dump(user_list, f)

# # 读取json
# with open('user_list.json', 'r') as f:
#     user_list = json.load(f)


# # post请求
# for i in user_list:
#     url = "http://127.0.0.1:8008/info"
#     data = {
#         "osuname": i,
#     }
#     response = requests.post(url, json=data)
#     result = response.json()
#     print(result)
