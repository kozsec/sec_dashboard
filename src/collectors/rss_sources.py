import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

import requests


CONFIG_FILE = "config/security_sources.json"
OUTPUT_DIR = "data"
JST = ZoneInfo("Asia/Tokyo")
HEADERS = {"User-Agent": "SecurityWatch/1.0 (+https://kozamon.com)"}


def local_datetime(value):
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(JST)


def text_value(element, names):
    for name in names:
        found = element.find(name)
        if found is not None and found.text:
            return found.text.strip()

    for child in list(element):
        if child.tag.rsplit("}", 1)[-1] in names and child.text:
            return child.text.strip()

    return ""


def parse_feed(content, source):
    root = ET.fromstring(content)
    entries = [
        node for node in root.iter()
        if node.tag.rsplit("}", 1)[-1] in ("item", "entry")
    ]

    articles = []

    for entry in entries:
        title = text_value(entry, ("title",))
        link = text_value(entry, ("link",))

        if not link:
            for child in list(entry):
                if child.tag.rsplit("}", 1)[-1] == "link":
                    link = child.attrib.get("href", "").strip()
                    if link:
                        break

        published = text_value(
            entry,
            ("pubDate", "published", "updated", "date")
        )

        if not title or not link:
            continue

        published_at = local_datetime(published)
        if not published_at:
            continue

        articles.append({
            "source": "海外" if source["region"] == "Overseas" else "国内",
            "date": published_at.strftime("%Y-%m-%d"),
            "time": published_at.strftime("%H:%M"),
            "organization": source["organization"],
            "identifier": None,
            "title": title,
            "url": link
        })

    return articles


def save_articles(articles):
    grouped = {}

    for article in articles:
        filename = os.path.join(
            OUTPUT_DIR,
            f"feed_{article['date'].replace('-', '')}.json"
        )
        grouped.setdefault(filename, []).append(article)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename, new_articles in grouped.items():
        existing = []

        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    existing = json.load(file)
                if not isinstance(existing, list):
                    existing = []
            except (OSError, json.JSONDecodeError):
                existing = []

        urls = {
            item.get("url")
            for item in existing
            if isinstance(item, dict)
        }

        added = [
            item for item in new_articles
            if item["url"] not in urls
        ]

        if not added:
            continue

        merged = existing + added
        merged.sort(
            key=lambda item: (
                item.get("date") or "",
                item.get("time") or ""
            ),
            reverse=True
        )

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(merged, file, ensure_ascii=False, indent=2)
            file.write("\n")

        print(f"{filename}: {len(added)}件追加")


def fetch_rss_sources():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        sources = json.load(file)

    articles = []

    for source in sources:
        print(f"RSS取得: {source['organization']}")

        try:
            response = requests.get(
                source["url"],
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            found = parse_feed(response.content, source)
            articles.extend(found)
            print(f"  {len(found)}件取得")
        except Exception as error:
            print(f"  取得失敗: {error}")

    save_articles(articles)


if __name__ == "__main__":
    fetch_rss_sources()
