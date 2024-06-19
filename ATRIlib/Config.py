import configparser
import os


class Config:
    def __init__(self):
        self.osuclientid = os.getenv('OSU_CLIENT_ID')
        self.osuclientsecret = os.getenv('OSU_CLIENT_SECRET')
        # mongoDB 应该可以直接用 url 的方式连接 ?
        self.mongodb_url = os.getenv('MONGO_URL')

        if self.osuclientid and self.osuclientsecret and self.mongodb_url:
            return

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        if not self.osuclientid:
            self.osuclientid = self.config['OSUAPI']['client_id']
        if not self.osuclientsecret:
            self.osuclientsecret = self.config['OSUAPI']['client_secret']
        if not self.mongodb_url:
            self.mongodb_url = "mongodb://localhost:27017"
