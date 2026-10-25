import requests
import re

# Target Settings
BASE_URL = "223.25.71.211:5001"
INPUT_M3U = "jtv.m3u"  # The file you already have
OUTPUT_M3U = "jtv_playable.m3u"

def steal_tokens():
    print("[*] Reading M3U and extracting Channel IDs...")
    
    try:
        with open(INPUT_M3U, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract all tvg-id values (e.g., 143, 476)
        channel_ids = re.findall(r'tvg-id="(\d+)"', content)
        # Extract channel names for the playlist labels
        channel_names = re.findall(r'group-title=".*?", (.*?)\n', content)

        if not channel_ids:
            print("[-] No IDs found! Make sure jtv.m3u is in the same folder.")
            return

        print(f"[+] Found {len(channel_ids)} channels. Generating auth tokens...")

        playable_list = ["#EXTM3U"]
        
        # Combine IDs and Names
        for cid, name in zip(channel_ids, channel_names):
            name = name.strip()
            # This is the endpoint that generates the auth token
            request_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            try:
                # We request the page. The server will redirect us to the URL containing the 'auth' token.
                # allow_redirects=True is key here.
                response = requests.get(request_url, allow_redirects=True, timeout=5)
                
                # The final URL in response.url will contain the ?auth=... string
                final_token_url = response.url
                
                if "auth=" in final_token_url:
                    playable_list.append(f"#EXTINF:-1, {name}")
                    playable_list.append(final_token_url)
                    print(f"[+] Success: {name} -> Token Captured")
                else:
                    print(f"[-] Failed: {name} (No auth token in response)")
            
            except Exception as e:
                print(f"[-] Error fetching {name}: {e}")

        # Save the working playlist
        with open(OUTPUT_M3U, 'w', encoding='utf-8') as f:
            f.write("\n".join(playable_list))

        print(f"\n[!] DONE! Your playable playlist is saved as: {OUTPUT_M3U}")
        print("[!] Open this file with VLC Media Player.")

    except FileNotFoundError:
        print(f"[-] Error: {INPUT_M3U} not found.")

if __name__ == "__main__":
    steal_tokens()
