import requests

url = "http://198.195.239.50/"

response = requests.get(url, timeout=15)

print("Status Code:", response.status_code)
print(response.text[:5000])

if response.status_code == 200 and (
    "#EXTM3U" in response.text
):
    with open("jtv.m3u", "w", encoding="utf-8", newline="") as f:
        f.write(response.text)

    print("Playlist exported!")
else:
    print("এটি সরাসরি M3U playlist নয়।")
