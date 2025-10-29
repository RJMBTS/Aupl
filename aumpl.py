import os
import datetime
import pytz
import requests

# File paths
MASTER_FILE = "Master.m3u"
AUSCL_FILE = "auscl.m3u"
INDEX_FILE = "Onetv.m3u"
CHANNELS_DIR = "channels"

# Ensure channels directory exists
os.makedirs(CHANNELS_DIR, exist_ok=True)


def generate_onetv_file():
    """Generate Onetv.m3u with local IST time and footer credits"""
    # Use India timezone
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")

    header = f"""#EXTM3U
# This channel file was auto-generated from Master.m3u
# Last updated on {timestamp}

"""

    footer = (
        "\n# --------------------------------------------------\n"
        "# Developed by Kittujk & Maintained by RJMBTS\n"
        "# --------------------------------------------------\n"
    )

    # Read content from Master.m3u
    if not os.path.exists(MASTER_FILE):
        print(f"❌ {MASTER_FILE} not found.")
        return

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Combine and write to Onetv.m3u
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(header + content + footer)

    print(f"✅ {INDEX_FILE} updated successfully at {timestamp}")


def main():
    print("🚀 Starting playlist update process...")

    # Example: clone Master.m3u into auscl.m3u
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r", encoding="utf-8") as f:
            data = f.readlines()

        with open(AUSCL_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for line in data:
                f.write(line)

        print(f"✅ {AUSCL_FILE} updated.")

    # Generate the main index playlist
    generate_onetv_file()

    print("✅ Playlist generation completed.")


if __name__ == "__main__":
    main()
