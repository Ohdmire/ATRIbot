# post请求
import requests

url = "http://127.0.0.1:8008/choke"
data = {
    "osuname": "ChocolateCR",
}

response = requests.post(url, json=data)
result = response.json()
print(result)
