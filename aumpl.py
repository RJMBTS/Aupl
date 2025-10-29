import requests
import re
import os
import shutil
import datetime

# 🔗 Remote playlist source
SOURCE_URL = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u"

# 📂 File paths
MASTER_FILE = "Master.m3u"
AUSCL_FILE = "auscl.m3u"
OUTPUT_DIR = "channels"
INDEX_FILE = "index.m3u"
TIMEOUT = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_source():
    print("🌐 Fetching source M3U…")
    r = requests.get(SOURCE_URL)
    r.raise_for_status()
    return r.text

def save_master(content):
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Saved {MASTER_FILE}")

def parse_channels(text):
    parts = text.split("#EXTINF")
    channels = []
    for p in parts:
        if not p.strip():
            continue
        entry = "#EXTINF" + p  # restore the marker
        lines = entry.strip().splitlines()
        name_match = re.search(r',([^,]+)$', lines[0])
        name = name_match.group(1).strip() if name_match else "Unknown"

        url = None
        for line in lines:
            if line.strip().startswith("http"):
                url = line.strip()
                break

        if url:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            full_entry = "\n".join(lines)
            channels.append({
                "name": name,
                "safe_name": safe_name,
                "url": url,
                "entry": full_entry
            })
    return channels

def save_channels(chans):
    ok, bad = [], []
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    for ch in chans:
        path = os.path.join(OUTPUT_DIR, f"{ch['safe_name']}.m3u8")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"# This channel file was auto-generated from Master.m3u on {timestamp}\n")
                f.write(f"# Source: {SOURCE_URL}\n\n")
                f.write(ch["entry"].strip() + "\n")
            ok.append(ch)
            print(f"✅ {ch['name']}")
        except Exception as e:
            print(f"❌ {ch['name']} ({e})")
            bad.append(ch)
    return ok, bad

def build_index(chans):
    lines = ["#EXTM3U"]
    for ch in chans:
        lines.append(f"#EXTINF:-1,{ch['name']}")
        lines.append(f"https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/channels/{ch['safe_name']}.m3u8")
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📃 index.m3u built ({len(chans)} entries)")

def duplicate_to_auscl():
    if os.path.exists(MASTER_FILE):
        shutil.copyfile(MASTER_FILE, AUSCL_FILE)
        print(f"📋 Copied Master.m3u → auscl.m3u")

def main():
    try:
        master = fetch_source()
        save_master(master)
        chans = parse_channels(master)
        print(f"🧩 Found {len(chans)} channels")
        ok, bad = save_channels(chans)
        build_index(ok)
        duplicate_to_auscl()
        print(f"\n✅ Done: {len(ok)} channels created, {len(bad)} failed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
