import os
import re
import datetime
import requests

# === CONFIG ===
MASTER_URL = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u"
CHANNELS_DIR = "channels"
INDEX_FILE = "index.m3u"
AUSCL_FILE = "auscl.m3u"
HTML_FILE = "index.html"


def fetch_master():
    print("🌐 Fetching Master.m3u...")
    response = requests.get(MASTER_URL)
    response.raise_for_status()
    return response.text


def parse_channels(master_text):
    channels = []
    blocks = master_text.split("#EXTINF:")
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        meta = lines[0]
        url = None
        for line in lines[1:]:
            if line.startswith("http"):
                url = line.strip()
                break
        if url:
            name = meta.split(",")[-1].strip()
            logo_match = re.search(r'tvg-logo="([^"]+)"', meta)
            logo = logo_match.group(1) if logo_match else ""
            channels.append((name, logo, "#EXTINF:" + meta + "\n" + "\n".join(lines[1:])))
    return channels


def write_channel_files(channels):
    os.makedirs(CHANNELS_DIR, exist_ok=True)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    for name, _, content in channels:
        safe_name = name.replace(" ", "_").replace("/", "_")
        file_path = os.path.join(CHANNELS_DIR, f"{safe_name}.m3u8")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# Last updated on {now}\n\n")
            f.write(content + "\n")
        print(f"✅ Created: {file_path}")


def write_auscl(channels):
    with open(AUSCL_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for _, _, content in channels:
            f.write(content + "\n")
    print("📄 auscl.m3u updated.")


def write_index(channels):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, _, _ in channels:
            f.write(f"#EXTINF:-1,{name}\n")
            f.write(f"https://nrtv-one.vercel.app/channels/{name.replace(' ', '_')}.m3u8\n")
    print("📃 index.m3u generated.")


def generate_html_index(channels):
    print("🖥️ Generating index.html...")
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Sort alphabetically by name
    channels = sorted(channels, key=lambda c: c[0].lower())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OneTV Channels</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      padding: 2rem;
      text-align: center;
    }}
    h1 {{
      color: #58a6ff;
      margin-bottom: 1rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 1rem;
      max-width: 1000px;
      margin: auto;
    }}
    .card {{
      background: #161b22;
      padding: 1rem;
      border-radius: 0.8rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }}
    img {{
      width: 90px;
      height: 90px;
      object-fit: contain;
      border-radius: 0.4rem;
      margin-bottom: 0.6rem;
      background: #0d1117;
    }}
    a {{
      color: #58a6ff;
      text-decoration: none;
      font-weight: 500;
      margin-bottom: 0.4rem;
      word-wrap: break-word;
    }}
    button {{
      background: #238636;
      color: white;
      border: none;
      border-radius: 0.3rem;
      padding: 0.4rem 0.8rem;
      cursor: pointer;
      transition: 0.2s;
    }}
    button:hover {{
      background: #2ea043;
    }}
    .footer {{
      margin-top: 2rem;
      font-size: 0.85rem;
      color: #8b949e;
    }}
  </style>
</head>
<body>
  <h1>📺 OneTV Channels</h1>
  <p>Click a channel to open or copy its link.</p>
  <div class="grid">
"""

    for name, logo, _ in channels:
        safe_name = name.replace(" ", "_")
        link = f"https://nrtv-one.vercel.app/channels/{safe_name}.m3u8"
        html += f"""
    <div class="card">
      <img src="{logo or 'https://via.placeholder.com/90x90?text=No+Logo'}" alt="{name} logo" />
      <a href="{link}" target="_blank">{name}</a>
      <button onclick="navigator.clipboard.writeText('{link}'); this.textContent='Copied!'; setTimeout(()=>this.textContent='Copy Link',2000);">Copy Link</button>
    </div>
"""

    html += f"""
  </div>
  <div class="footer">
    Last updated on {now}
  </div>
</body>
</html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html generated with logos, copy buttons, and alphabetical order.")


if __name__ == "__main__":
    master = fetch_master()
    channels = parse_channels(master)
    write_channel_files(channels)
    write_auscl(channels)
    write_index(channels)
    generate_html_index(channels)
    print("🎉 All tasks complete successfully!")
