import requests
from bs4 import BeautifulSoup
import re

# Target configuration
TARGET_URL = "http://223.25.71.211:5001"
OUTPUT_FILE = "playlist.m3u"

def extract_media():
    print(f"[*] Initiating crawl on {TARGET_URL}...")
    try:
        # Send request with a spoofed User-Agent to avoid basic bot detection
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[-] Target returned status code: {response.status_code}")
            return

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Regex to find audio files (mp3, wav, ogg, m4a)
        audio_pattern = re.compile(r'.*\.(mp3|wav|ogg|m4a)', re.IGNORECASE)
        links = []

        # Search for all <a> tags and <img> tags (sometimes media is hidden in src)
        for tag in soup.find_all(['a', 'img', 'source'], src=True):
            link = tag.get('src') or tag.get('href')
            if link and audio_pattern.match(link):
                # Ensure the link is absolute
                full_url = link if link.startswith('http') else f"{TARGET_URL}/{link}"
                links.append(full_url)

        # Also search for raw strings in the page source (for hidden API links)
        raw_links = re.findall(r'https?://\S*\.(?:mp3|wav|ogg|m4a)', response.text)
        links.extend(raw_links)

        # Remove duplicates
        unique_links = list(set(links))

        if not unique_links:
            print("[-] No media links found. The target might be using a JSON API or JS rendering.")
            return

        # Write to M3U Playlist format
        with open(OUTPUT_FILE, "w") as f:
            f.write("#EXTM3U\n")
            for link in unique_links:
                f.write(f"#EXTINF:-1, Track\n{link}\n")
        
        print(f"[+] Success! {len(unique_links)} tracks extracted to {OUTPUT_FILE}")

    except Exception as e:
        print(f"[-] Execution error: {e}")

if __name__ == "__main__":
    extract_media()
