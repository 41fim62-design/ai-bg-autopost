import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ.get("CHAT_ID", "@AI_BG")
FILE = Path("seen.json")

QUERY = "искусственный интеллект OR нейросети OR робототехника"
URL = "https://news.google.com/rss/search?q=" + urllib.parse.quote(QUERY) + "&hl=ru&gl=RU&ceid=RU:ru"

seen_list = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else []
seen = set(seen_list)

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as response:
    root = ET.fromstring(response.read())

def clean_html(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()

def category_for(title):
    t = title.lower()
    if any(w in t for w in ("робот", "робототех", "дрон")):
        return "🤖 Робототехника"
    if any(w in t for w in ("чатгпт", "chatgpt", "gpt", "язык", "llm")):
        return "💬 ИИ и языковые модели"
    if any(w in t for w in ("нейросет", "генерац", "изображен", "видео")):
        return "🎨 Нейросети и генерация"
    return "🧠 Искусственный интеллект"

count = 0
new_seen = []

for item in root.findall("./channel/item"):
    title = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()

    if not title or not link or link in seen:
        continue

    description = clean_html(item.findtext("description", ""))
    source_node = item.find("source")
    source = source_node.text.strip() if source_node is not None and source_node.text else "Источник в ссылке"

    parts = [
        f"🤖 {title}",
        "",
        category_for(title),
    ]

    if description:
        snippet = description[:420].rsplit(" ", 1)[0]
        parts += ["", "📌 Кратко:", snippet]

    parts += [
        "",
        f"📰 Источник: {source}",
        f"🔗 {link}",
        "",
        "#ИИ #технологии"
    ]

    message = "\n".join(parts)

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": "false",
    }).encode()

    api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    with urllib.request.urlopen(api, data=data, timeout=30) as response:
        result = json.loads(response.read())

    if not result.get("ok"):
        raise RuntimeError(result)

    seen.add(link)
    new_seen.append(link)
    count += 1

    if count >= 3:
        break

updated_seen = (seen_list + new_seen)[-1000:]

FILE.write_text(
    json.dumps(updated_seen, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Опубликовано: {count}")