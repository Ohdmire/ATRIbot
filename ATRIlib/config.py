import configparser
import os

osuclientid = os.getenv('OSU_CLIENT_ID')
osuclientsecret = os.getenv('OSU_CLIENT_SECRET')
# mongoDB 应该可以直接用 url 的方式连接 ?
mongodb = os.getenv('MONGO_URI')

if osuclientid and osuclientsecret:
    print('从环境变量获取')
else:
    print('从配置文件获取')

    config = configparser.ConfigParser()
    config.read('config.ini')

    if not osuclientid:
        osuclientid = config['OSUAPI']['client_id']
    if not osuclientsecret:
        osuclientsecret = config['OSUAPI']['client_secret']
