import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ.get("CHAT_ID", "@AI_BG")
FILE = Path("seen.json")

URL = "https://news.google.com/rss/search?q=" + urllib.parse.quote(
    "искусственный интеллект OR нейросети OR робототехника"
) + "&hl=ru&gl=RU&ceid=RU:ru"

seen = set(json.loads(FILE.read_text()) if FILE.exists() else [])

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as response:
    root = ET.fromstring(response.read())

count = 0

for item in root.findall("./channel/item"):
    title = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()

    if not title or not link or link in seen:
        continue

    text = f"🤖 {title}\n\n📰 Новости ИИ\n🔗 {link}\n\n#ИИ #нейросети"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text
    }).encode()

    api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    with urllib.request.urlopen(api, data=data, timeout=30) as response:
        result = json.loads(response.read())

    if not result.get("ok"):
        raise RuntimeError(result)

    seen.add(link)
    count += 1

    if count >= 3:
        break

FILE.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2))
print(f"Опубликовано: {count}")
