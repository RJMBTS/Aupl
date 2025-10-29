import requests
import os
from datetime import datetime
import pytz

# ----------------------------
# Configuration
# ----------------------------
MASTER_URL = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u"
CHANNELS_DIR = "channels"
AUSCL_FILE = "auscl.m3u"
ONETV_FILE = "Onetv.m3u"  # renamed from index.m3u
TIMEZONE = pytz.timezone("Asia/Kolkata")  # UTC+5:30

# ----------------------------
# Utility functions
# ----------------------------
def fetch_master():
    print("Fetching latest Master.m3u...")
    response = requests.get(MASTER_URL)
    response.raise_for_status()
    return response.text

def parse_channels(text):
    lines = text.strip().splitlines()
    channels = []
    current_meta = []

    for line in lines:
        if line.startswith("#EXTINF"):
            current_meta = [line]
        elif line.startswith("#KODIPROP") or line.startswith("#EXTVLCOPT") or line.startswith("#EXTHTTP"):
            current_meta.append(line)
        elif line.startswith("http"):
            # Finalize one channel block
            current_meta.append(line)
            channels.append("\n".join(current_meta))
            current_meta = []
    return channels

# ----------------------------
# File generation
# ----------------------------
def write_channel_files(channels):
    if not os.path.exists(CHANNELS_DIR):
        os.makedirs(CHANNELS_DIR)

    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S %Z%z")

    for i, channel_data in enumerate(channels, start=1):
        channel_name = None
        for line in channel_data.splitlines():
            if line.startswith("#EXTINF"):
                channel_name = line.split(",")[-1].strip().replace(" ", "_").replace("/", "_")
                break
        if not channel_name:
            channel_name = f"Channel_{i}"

        filename = f"{channel_name}.m3u8"
        filepath = os.path.join(CHANNELS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# This channel file was auto-generated from Master.m3u\n")
            f.write(f"# Last updated on {timestamp}\n\n")
            f.write(channel_data + "\n")
        print(f"✅ {filename} generated.")

def write_master_variants(master_text):
    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S %Z%z")

    # auscl.m3u
    with open(AUSCL_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Auto-updated from Master.m3u\n")
        f.write(f"# Last updated on {timestamp}\n\n")
        f.write(master_text)

    # Onetv.m3u (main entry list)
    if not os.path.exists(CHANNELS_DIR):
        os.makedirs(CHANNELS_DIR)

    channel_files = [f for f in os.listdir(CHANNELS_DIR) if f.endswith(".m3u8")]

    with open(ONETV_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# OneTV Master Playlist\n")
        f.write(f"# Last updated on {timestamp}\n\n")
        for ch in channel_files:
            name = ch.replace(".m3u8", "").replace("_", " ")
            f.write(f"#EXTINF:-1,{name}\n")
            f.write(f"https://nrtv-one.vercel.app/channels/{ch}\n\n")

# ----------------------------
# Main workflow
# ----------------------------
def main():
    try:
        master_text = fetch_master()
        channels = parse_channels(master_text)
        write_channel_files(channels)
        write_master_variants(master_text)
        print("\n🎉 All files generated and updated successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
