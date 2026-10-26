import requests

ip = "103.16.24.4:8083"

playlist = requests.get(f"http://{ip}/playlist.m3u")

print(playlist.text)

with open('./jtv.m3u', 'w', newline='') as f:
    f.write(playlist.text)
    print("Exported!")

f.close()
