import os
import datetime
import requests

# === CONFIG ===
MASTER_URL = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u"
CHANNELS_DIR = "channels"
INDEX_FILE = "index.m3u"
AUSCL_FILE = "auscl.m3u"
HTML_FILE = "index.html"


def fetch_master():
    print("Fetching Master.m3u...")
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
            channels.append((name, "#EXTINF:" + meta + "\n" + "\n".join(lines[1:])))
    return channels


def write_channel_files(channels):
    os.makedirs(CHANNELS_DIR, exist_ok=True)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    for name, content in channels:
        safe_name = name.replace(" ", "_").replace("/", "_")
        file_path = os.path.join(CHANNELS_DIR, f"{safe_name}.m3u8")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# This channel file was auto-generated on {now}\n\n")
            f.write(content + "\n")
        print(f"✅ Generated {file_path}")


def write_auscl(channels):
    with open(AUSCL_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for _, content in channels:
            f.write(content + "\n")


def write_index(channels):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, _ in channels:
            f.write(f"#EXTINF:-1,{name}\n")
            f.write(f"https://nrtv-one.vercel.app/channels/{name.replace(' ', '_')}.m3u8\n")


def generate_html_index():
    print("Generating index.html...")
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    files = [f for f in os.listdir(CHANNELS_DIR) if f.endswith(".m3u8")]
    files.sort()

    html_content = f"""<!DOCTYPE html>
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
    ul {{
      list-style: none;
      padding: 0;
      max-width: 600px;
      margin: auto;
    }}
    li {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #161b22;
      margin: 0.5rem 0;
      padding: 0.7rem 1rem;
      border-radius: 0.5rem;
    }}
    a {{
      color: #58a6ff;
      text-decoration: none;
      word-break: break-word;
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
  <p>Click a channel name to open or copy its link below.</p>

  <ul>
"""

    for f in files:
        name = os.path.splitext(f)[0]
        link = f"/channels/{f}"
        html_content += f"""
    <li>
      <a href="{link}" target="_blank">{name}</a>
      <button onclick="navigator.clipboard.writeText('{f'https://nrtv-one.vercel.app{link}'}'); this.textContent='Copied!'; setTimeout(()=>this.textContent='Copy Link',2000);">Copy Link</button>
    </li>
"""

    html_content += f"""
  </ul>

  <div class="footer">
    Last updated on {now}
  </div>
</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html updated.")


if __name__ == "__main__":
    master = fetch_master()
    channels = parse_channels(master)
    write_channel_files(channels)
    write_auscl(channels)
    write_index(channels)
    generate_html_index()
    print("🎉 All tasks complete!")
