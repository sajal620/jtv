import requests

ip = "103.151.60.188:12345"

playlist = requests.get(f"http://{ip}/playlist.m3u")

print(playlist.text)

with open('./jtv.m3u', 'w', newline='') as f:
    f.write(playlist.text)
    print("Exported!")

f.close()
