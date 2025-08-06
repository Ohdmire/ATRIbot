import os

osuclientid = os.getenv('OSU_CLIENT_ID')
osuclientsecret = os.getenv('OSU_CLIENT_SECRET')
mongodb_uri = os.getenv('MONGO_URI')
deepseek_key = os.getenv('DEEPSEEK_KEY')
pppclientid = os.getenv('PPP_CLIENT_ID')
pppclientsecret = os.getenv('PPP_CLIENT_SECRET')

try:
    with open("translate_prompt.txt", 'r') as f:
        translate_prompt = f.read()
except:
    translate_prompt = ""

# 确保所有必要的配置都已设置
assert osuclientid, "OSU Client ID 未设置"
assert osuclientsecret, "OSU Client Secret 未设置"
assert mongodb_uri, "MongoDB URI 未设置"


print(f"MongoDB URI: {mongodb_uri}")
