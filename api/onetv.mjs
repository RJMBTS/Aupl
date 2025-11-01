export default async function handler(req, res) {
  const masterUrl = "https://raw.githubusercontent.com/RJMBTS/Aupl/refs/heads/main/Master.m3u";
  try {
    const response = await fetch(masterUrl, { cache: "no-store" });
    if (!response.ok) throw new Error("Failed to fetch Master.m3u");

    const data = await response.text();
    res.setHeader("Content-Type", "audio/x-mpegurl; charset=utf-8");
    res.setHeader("Cache-Control", "no-cache");
    res.status(200).send(data);
  } catch (err) {
    res.status(500).send(`#EXTM3U\n# Error fetching Master.m3u\n# ${err.message}`);
  }
}
