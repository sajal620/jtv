import requests
import re

# Target Config
BASE_URL = "http://223.25.71.211:5001"
M3U_FILE = "jtv.m3u" # The file you exported earlier

def generate_playable_links():
    print("[*] Analyzing M3U for Channel IDs...")
    
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract tvg-id="XXX"
        channel_ids = re.findall(r'tvg-id="(\d+)"', content)
        # Extract channel names
        channel_names = re.findall(r'group-title=".*?", (.*)', content)

        if not channel_ids:
            print("[-] No Channel IDs found in the file.")
            return

        print(f"[+] Found {len(channel_ids)} channels. Attempting to generate tokens...")

        final_links = ["#EXTM3U"]
        
        # Map names to IDs
        channels = zip(channel_ids, channel_names)

        for cid, name in channels:
            # This is the magic endpoint you discovered
            # We attempt to hit it to see if it gives us a direct stream
            test_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            try:
                # We follow redirects to get the final URL with the 'auth' token
                res = requests.get(test_url, allow_redirects=True, timeout=5)
                final_url = res.url # This captures the ?auth=... part
                
                final_links.append(f"#EXTINF:-1, {name}")
                final_links.append(final_url)
                print(f"[+] Success: {name} (ID: {cid}) -> Token Captured")
            except:
                print(f"[-] Failed to get token for {name}")

        # Save to a new file that actually works in VLC/OTT players
        with open('jtv_working.m3u', 'w', encoding='utf-8') as f:
            f.write("\n".join(final_links))
            
        print("\n[!] DONE: 'jtv_working.m3u' created. Try playing this in VLC.")

    except FileNotFoundError:
        print(f"[-] Error: {M3U_FILE} not found. Run your first script first.")

if __name__ == "__main__":
    generate_playable_links()
