import requests
import re

# Target Settings
BASE_URL = "223.25.71.211:5001"
INPUT_M3U = "jtv.m3u"
OUTPUT_M3U = "jtv_playable.m3u"

# Using a high-end Browser Header to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

def extract_token_deep_scan(text):
    """
    Scans the response text for any string following 'auth=' 
    or any long base64-style string that looks like a token.
    """
    # Pattern 1: Explicitly look for auth=TOKEN
    match = re.search(r'auth=([a-zA-Z0-9\-_=]+)', text)
    if match:
        return match.group(1)
    
    # Pattern 2: Look for JSON style "auth":"TOKEN"
    match = re.search(r'"auth"\s*:\s*"([a-zA-Z0-9\-_=]+)"', text)
    if match:
        return match.group(1)
    
    return None

def steal_tokens():
    print("[*] Starting Precision Token Extraction...")
    
    try:
        with open(INPUT_M3U, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract IDs and Names from M3U
        channels = re.findall(r'tvg-id="(\d+)".*?,(.*)\n', content)

        if not channels:
            print("[-] No IDs found in jtv.m3u!")
            return

        print(f"[+] Found {len(channels)} channels. Generating links...")

        playable_list = ["#EXTM3U"]
        session = requests.Session()
        session.headers.update(HEADERS)

        for cid, name in channels:
            name = name.strip()
            # This is the request we send to trigger the token generation
            trigger_url = f"{BASE_URL}/render.m3u8?channel_key_id={cid}&q=auto"
            
            try:
                # We get the response and allow redirects to follow the trail
                response = session.get(trigger_url, timeout=10, allow_redirects=True)
                
                # 1. Check the final URL for the token (Redirect Method)
                token = extract_token_deep_scan(response.url)
                
                # 2. If not in URL, scan the body (JSON/HTML Method)
                if not token:
                    token = extract_token_deep_scan(response.text)

                if token:
                    # CONSTRUCT THE EXACT LINK YOU WANT
                    final_playable_url = f"{BASE_URL}/render.m3u8?auth={token}&channel_key_id={cid}&q=auto"
                    
                    playable_list.append(f"#EXTINF:-1, {name}")
                    playable_list.append(final_playable_url)
                    print(f"[+] SUCCESS: {name} -> Link Generated")
                else:
                    print(f"[-] FAILED: {name} (Token not found in response)")

            except Exception as e:
                print(f"[-] Error on {name}: {e}")

        # Save the final M3U file
        with open(OUTPUT_M3U, 'w', encoding='utf-8') as f:
            f.write("\n".join(playable_list))

        print(f"\n[!] DONE! Your playable playlist is saved as: {OUTPUT_M3U}")

    except FileNotFoundError:
        print(f"[-] Error: {INPUT_M3U} not found.")

if __name__ == "__main__":
    steal_tokens()
