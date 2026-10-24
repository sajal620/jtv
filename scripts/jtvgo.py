
import json
import os
import re
import requests

SOURCE_URL = "http://198.195.239.50/tv_channels.json"
OUTPUT_FILE = "jtv.m3u"
TIMEOUT = 30


def get_text(data, *keys):
    """Return the first non-empty string found in the given keys."""
    if not isinstance(data, dict):
        return ""

    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def find_stream_url(channel):
    """Find a stream URL in common JSON structures."""
    if isinstance(channel, str):
        return channel.strip()

    if not isinstance(channel, dict):
        return ""

    url = get_text(
        channel,
        "url",
        "stream_url",
        "streamUrl",
        "stream",
        "link",
        "src",
        "play_url",
        "playUrl",
        "m3u8",
    )

    if url:
        return url

    for key in ("sources", "streams", "playlists", "urls"):
        sources = channel.get(key)

        if isinstance(sources, str):
            return sources.strip()

        if isinstance(sources, list):
            for source in sources:
                found = find_stream_url(source)
                if found:
                    return found

        if isinstance(sources, dict):
            found = find_stream_url(sources)
            if found:
                return found

    return ""


def extract_channels(data):
    """Support common JSON list and dictionary layouts."""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("channels", "tv_channels", "data", "results", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value

        # A single channel object
        if find_stream_url(data):
            return [data]

    raise ValueError(
        "Could not identify the channel list in the JSON response."
    )


def clean_attribute(value):
    """Prevent line breaks and quotes from breaking M3U attributes."""
    return re.sub(r'[\r\n"]', "", str(value or "")).strip()


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 PlaylistGenerator/1.0",
        "Accept": "application/json",
    }

    response = requests.get(
        SOURCE_URL,
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    channels = extract_channels(data)

    lines = ["#EXTM3U"]
    added = 0

    for channel in channels:
        if not isinstance(channel, dict):
            continue

        name = get_text(channel, "name", "title", "channel_name")
        if not name:
            name = f"Channel {added + 1}"

        stream_url = find_stream_url(channel)

        # Do not export entries without a stream URL.
        if not stream_url:
            continue

        # Only export HTTP(S) stream URLs.
        if not stream_url.startswith(("http://", "https://")):
            continue

        logo = get_text(
            channel, "logo", "logo_url", "image", "icon"
        )
        category = get_text(
            channel, "category", "group", "group_title"
        )

        attributes = []

        if category:
            attributes.append(
                f'group-title="{clean_attribute(category)}"'
            )

        if logo.startswith(("http://", "https://")):
            attributes.append(
                f'tvg-logo="{clean_attribute(logo)}"'
            )

        attribute_text = (
            " " + " ".join(attributes) if attributes else ""
        )

        lines.append(f"#EXTINF:-1{attribute_text},{name}")
        lines.append(stream_url)
        added += 1

    if added == 0:
        raise ValueError(
            "No usable stream URLs found. "
            "Check the JSON structure before replacing the playlist."
        )

    # Write only after successful parsing and validation.
    temp_file = OUTPUT_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")

    os.replace(temp_file, OUTPUT_FILE)

    print(f"Exported {added} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
