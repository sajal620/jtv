import requests
import re

# Target Config
BASE_URL = "223.25.71.211:5001"
# If the site requires login, put your cookies here (Get them from F12 -> Application -> Cookies)
COOKIES = {
    "session_id": "YOUR_SESSION_ID_HERE" 
}

def get_active_playlist():
    print("[*] Attempting to intercept dynamic stream tokens...")
    
    try:
        # 1. Get the base playlist to find channel IDs
        response = requests.get(f"{BASE_URL}/playlist.m3u", cookies=COOKIES)
        content = response.text
        
        # 2. Find all channel key IDs or patterns that look like channel links
        # This regex looks for things like 'channel_key_id=XXX'
        channel_ids = re.findall(r'channel_key_id=(\d+)', content)
        
        if not channel_ids:
            # If not in the m3u, try searching the main page HTML
            page_res = requests.get(BASE_URL, cookies=COOKIES)
            channel_ids = re.findall(r'channel_key_id=(\d+)', page_res.text)

        if not channel_ids:
            print("[-] No Channel IDs found. The server might be using encrypted tokens.")
            return

        print(f"[+] Found {len(channel_ids)} potential channels. Generating authenticated links...")

        final_playlist = ["#EXTM3U"]
        
        for cid in set(channel_ids):
            # This is the critical part: we simulate the request that the web player makes
            # We try to hit the render endpoint to get the current token
            token_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            # We hit the URL to see if it redirects or provides a tokenized link
            token_res = requests.get(token_url, cookies=COOKIES, allow_redirects=True)
            
            if token_res.status_code == 200:
                # If the response is a redirect, the 'url' property contains the final tokenized link
                final_link = token_res.url 
                final_playlist.append(f"#EXTINF:-1, Channel {cid}")
                final_playlist.append(final_link)
                print(f"[+] Captured token for Channel {cid}")

        # 3. Export to file
        with open('jtv_dynamic.m3u', 'w') as f:
            f.write("\n".join(final_playlist))
            
        print("\n[!] Success: jtv_dynamic.m3u has been generated with active tokens.")

    except Exception as e:
        print(f"[-] Critical Error: {e}")

if __name__ == "__main__":
    get_active_playlist()
