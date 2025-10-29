import requests
import re
import os
import shutil

# 🔗 Remote playlist source
SOURCE_URL = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u"

# 📂 File paths
MASTER_FILE = "Master.m3u"
AUSCL_FILE = "auscl.m3u"
OUTPUT_DIR = "channels"
INDEX_FILE = "index.m3u"
TIMEOUT = 5  # seconds

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
    pattern = re.compile(r'#EXTINF:-1\s+(.*?)\n(https?://[^\s]+)')
    matches = pattern.findall(text)
    chans = []
    for meta, url in matches:
        name_match = re.search(r',([^,]+)$', meta.strip())
        name = name_match.group(1).strip() if name_match else "Unknown"
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        chans.append({"name": name, "safe_name": safe_name, "url": url})
    return chans

def validate_url(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code == 200
    except requests.RequestException:
        return False

def save_channels(chans):
    ok, bad = [], []
    for ch in chans:
        print(f"🔍 {ch['name']} …", end=" ")
        if validate_url(ch["url"]):
            path = os.path.join(OUTPUT_DIR, f"{ch['safe_name']}.m3u8")
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"#EXTINF:-1,{ch['name']}\n{ch['url']}\n")
            print("✅")
            ok.append(ch)
        else:
            print("❌")
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
    """Create a synced copy of Master.m3u as auscl.m3u."""
    if os.path.exists(MASTER_FILE):
        shutil.copyfile(MASTER_FILE, AUSCL_FILE)
        print(f"📋 Copied Master.m3u → auscl.m3u")

def main():
    try:
        master = fetch_source()
        save_master(master)
        chans = parse_channels(master)
        print(f"🧩 Found {len(chans)} total channels")
        ok, bad = save_channels(chans)
        build_index(ok)
        duplicate_to_auscl()
        print("\n📊 SUMMARY")
        print(f"✅ Working channels: {len(ok)}")
        print(f"❌ Skipped channels: {len(bad)}")
        print(f"📁 Total created: {len(ok)}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
