# post请求
import requests

pp_list = [200]


url = "http://127.0.0.1:8008/addpp"
data = {
    "osuname": "ATRI1024",
    "pp_list": pp_list
}

response = requests.post(url, json=data)
result = response.json()
print(result)
