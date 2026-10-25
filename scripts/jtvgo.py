import requests
import re
import json

# Target Settings
BASE_URL = "223.25.71.211:5001"
INPUT_M3U = "jtv.m3u"
OUTPUT_M3U = "jtv_playable.m3u"

# We must use a real browser User-Agent to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

def steal_tokens():
    print("[*] Starting Advanced Token Extraction...")
    
    try:
        with open(INPUT_M3U, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract IDs and Names using a more flexible regex
        # This looks for tvg-id="123" and captures the name after the comma
        channels = re.findall(r'tvg-id="(\d+)".*?,(.*)\n', content)

        if not channels:
            print("[-] No channel IDs found in jtv.m3u. Check the file format!")
            return

        print(f"[+] Target list loaded: {len(channels)} channels found.")
        
        # Use a session to maintain cookies (some servers require a session cookie to give a token)
        session = requests.Session()
        session.headers.update(HEADERS)

        playable_list = ["#EXTM3U"]
        
        for cid, name in channels:
            name = name.strip()
            request_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            try:
                # We fetch the page and let it redirect
                response = session.get(request_url, timeout=10, allow_redirects=True)
                
                # DEBUG: If you still get nothing, uncomment the line below to see what the server is actually sending
                # print(f"DEBUG {name}: {response.text[:200]}") 

                token = None

                # 1. Search for token in the final URL (Redirect method)
                if "auth=" in response.url:
                    # Extract everything after auth= up to the next & or end of string
                    token_match = re.search(r'auth=([^&]+)', response.url)
                    if token_match:
                        token = token_match.group(1)

                # 2. Search for token in the response BODY (JSON or Text method)
                if not token:
                    body_match = re.search(r'auth=([a-zA-Z0-9\-_=]+)', response.text)
                    if body_match:
                        token = body_match.group(1)
                
                # 3. Try parsing as JSON if it looks like JSON
                if not token and response.text.strip().startswith('{'):
                    try:
                        data = response.json()
                        token = data.get('auth') or data.get('token')
                    except:
                        pass

                if token:
                    # Construct the exact playable URL format
                    final_url = f"{BASE_URL}/render.m3u8?auth={token}&channel_key_id={cid}&q=auto"
                    playable_list.append(f"#EXTINF:-1, {name}")
                    playable_list.append(final_url)
                    print(f"[+] SUCCESS: {name} -> Token Snagged")
                else:
                    print(f"[-] FAILED: {name} - Server didn't return a token.")

            except Exception as e:
                print(f"[-] Error on {name}: {e}")

        with open(OUTPUT_M3U, 'w', encoding='utf-8') as f:
            f.write("\n".join(playable_list))

        print(f"\n[!] DONE! File saved as: {OUTPUT_M3U}")

    except FileNotFoundError:
        print(f"[-] Error: {INPUT_M3U} not found.")

if __name__ == "__main__":
    steal_tokens()
