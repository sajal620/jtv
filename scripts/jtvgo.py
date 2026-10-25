import requests
import re
import json

# Target Settings
BASE_URL = "223.25.71.211:5001"
INPUT_M3U = "jtv.m3u"
OUTPUT_M3U = "jtv_playable.m3u"

def steal_tokens():
    print("[*] Initiating Token Extraction Ops...")
    
    try:
        with open(INPUT_M3U, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract tvg-id and channel names
        # Improved regex to capture name accurately from M3U format
        channels = re.findall(r'#EXTINF:-1.*?tvg-id="(\d+)".*?,(.*)\n', content)

        if not channels:
            print("[-] No channel data found! Check your jtv.m3u file.")
            return

        print(f"[+] Found {len(channels)} targets. Cracking auth tokens...")

        playable_list = ["#EXTM3U"]
        
        for cid, name in channels:
            name = name.strip()
            # The trigger URL
            request_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            try:
                # We set allow_redirects=False first to see if the token is in the header or body
                response = requests.get(request_url, timeout=10)
                
                token = None
                
                # Method 1: Check if response is JSON
                try:
                    data = response.json()
                    if 'auth' in data:
                        token = data['auth']
                except json.JSONDecodeError:
                    # Method 2: Regex search in the response body for auth=...
                    match = re.search(r'auth=([a-zA-Z0-9\-_=]+)', response.text)
                    if match:
                        token = match.group(1)

                if token:
                    # Construct the exact URL format you provided
                    final_url = f"{BASE_URL}/render.m3u8?auth={token}&channel_key_id={cid}&q=auto"
                    playable_list.append(f"#EXTINF:-1, {name}")
                    playable_list.append(final_url)
                    print(f"[+] Captured: {name} | Token: {token[:10]}...")
                else:
                    print(f"[-] Failed: {name} (No token found in response body)")
            
            except Exception as e:
                print(f"[-] Connection Error on {name}: {e}")

        # Dump to file
        with open(OUTPUT_M3U, 'w', encoding='utf-8') as f:
            f.write("\n".join(playable_list))

        print(f"\n[!] OPERATION COMPLETE. Playable list saved to: {OUTPUT_M3U}")

    except FileNotFoundError:
        print(f"[-] Critical Error: {INPUT_M3U} missing.")

if __name__ == "__main__":
    steal_tokens()
