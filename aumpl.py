import re
from datetime import datetime
import pytz

# Paths
m3u_file = "Onetv.m3u"
html_file = "index.html"

# Read the M3U playlist
with open(m3u_file, "r", encoding="utf-8") as f:
    m3u_content = f.read()

# Regex to extract channel info (tvg-logo, group-title, name, URL)
pattern = re.compile(
    r'#EXTINF:-1\s+(?:tvg-id="(?P<id>[^"]*)"\s*)?(?:group-title="(?P<group>[^"]*)"\s*)?(?:tvg-logo="(?P<logo>[^"]*)"\s*)?,(?P<name>[^\n]*)\n(?P<url>https?://[^\s]+)',
    re.MULTILINE
)

channels = pattern.findall(m3u_content)

# Generate channel cards
channel_cards = ""
for ch in channels:
    logo = ch[2] or "https://via.placeholder.com/90?text=Logo"
    name = ch[3].strip()
    url = ch[4].strip()
    group = ch[1] or "General"

    channel_cards += f"""
    <div class="card" data-name="{name.lower()}">
      <img src="{logo}" alt="{name}" />
      <a href="{url}" target="_blank">{name}</a>
      <button onclick="window.open('{url}', '_blank')">▶ Watch</button>
    </div>
    """

# Get current UTC+5:30 time
utc_now = datetime.utcnow()
ist = pytz.timezone("Asia/Kolkata")
current_time = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S UTC+5:30")

# Read index.html
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace channel grid and timestamp
html_content = re.sub(
    r'(<div class="grid" id="channelGrid">).*?(</div>\s*<div class="footer">)',
    rf'\1{channel_cards}\2',
    html_content,
    flags=re.DOTALL
)

html_content = re.sub(
    r'(Last updated on ).*?UTC[+]?\d*:?(\d*)',
    f"Last updated on {formatted_time}",
    html_content
)

# Write updated file
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Updated {html_file} with {len(channels)} channels at {formatted_time}")
