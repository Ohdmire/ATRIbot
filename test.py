# post请求
import requests

pp_list = [200]


url = "http://127.0.0.1:8008/bpsimvs"
data = {
    "osuname": "ATRI1024",
    "vs_name": "4001"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
