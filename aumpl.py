import os
import re
import pytz
from datetime import datetime

# --- File paths ---
MASTER_FILE = "Master.m3u"
OUTPUT_MASTER = "Onetv.m3u"
CHANNELS_DIR = "channels"

# --- Ensure output directory ---
os.makedirs(CHANNELS_DIR, exist_ok=True)

# --- Read Master.m3u ---
if not os.path.exists(MASTER_FILE):
    raise FileNotFoundError(f"{MASTER_FILE} not found")

with open(MASTER_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# --- Regex pattern to capture full channel blocks ---
pattern = r'(#EXTINF:-1[^\n]*\n(?:#KODIPROP[^\n]*\n)*#EXTVLCOPT[^\n]*\n(?:#EXTHTTP[^\n]*\n)?https?://[^\n]+)'
matches = re.findall(pattern, content)

# --- Get Indian time (UTC+5:30) ---
india_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z%z")

# --- Write combined Onetv.m3u ---
with open(OUTPUT_MASTER, "w", encoding="utf-8") as out:
    out.write("#EXTM3U\n")
    out.write(f"# Developed by Kittujk — Last updated on {india_time}\n\n")

    for block in matches:
        out.write(block.strip() + "\n\n")

        # --- Extract channel name ---
        name_match = re.search(r',(.+)$', block, re.MULTILINE)
        if name_match:
            name = re.sub(r'[^a-zA-Z0-9_-]', '_', name_match.group(1))
            chan_file = os.path.join(CHANNELS_DIR, f"{name}.m3u8")

            with open(chan_file, "w", encoding="utf-8") as cf:
                cf.write("#EXTM3U\n")
                cf.write(f"# Last updated on {india_time}\n\n")
                cf.write(block.strip() + "\n")

print(f"✅ Successfully generated {len(matches)} channels.")
