import requests

url = "http://198.195.239.50/tv_channels.json"

response = requests.get(url, timeout=20)
response.raise_for_status()

print(response.text[:10000])

with open("tv_channels.json", "w", encoding="utf-8") as f:
    f.write(response.text)

print("JSON exported!")
