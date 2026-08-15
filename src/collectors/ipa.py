import json
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

IPA_URL = "https://www.ipa.go.jp/news/index.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_ipa():
    today = datetime.now().strftime("%Y-%m-%d")

    response = requests.get(
        IPA_URL,
        timeout=30,
        headers=HEADERS
    )
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    items = []

    for link in soup.find_all("a", href=True):

        text = link.get_text(" ", strip=True)

        if not text:
            continue

        identifier = None

        if "セキュリティ" in text:
            identifier = "セキュリティ"

        elif "試験情報" in text:
            identifier = "試験情報"

        elif "人材育成" in text:
            identifier = "人材育成"

        else:
            continue

        href = link.get("href")

        if not href:
            continue

        url = urljoin(
            IPA_URL,
            href
        )

        date = extract_date(text)

        if not date:
            continue

        if date != today:
            continue

        title = text

        title = title.replace(
            identifier,
            "",
            1
        ).strip()

        item = {
            "source": "IPA",
            "date": date,
            "time": None,
            "organization": "IPA",
            "identifier": identifier,
            "title": title,
            "url": url
        }

        if item not in items:
            items.append(item)

    print(f"IPA updates: {len(items)}")

    save_json(items)

    return items


def extract_date(text):
    match = re.search(
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",
        text
    )

    if not match:
        return None

    year = match.group(1)
    month = match.group(2).zfill(2)
    day = match.group(3).zfill(2)

    return f"{year}-{month}-{day}"


def save_json(data):
    if not data:
        print("No IPA updates.")
        return

    date_str = data[0]["date"].replace("-", "")

    filename = f"data/feed_{date_str}.json"

    os.makedirs(
        "data",
        exist_ok=True
    )

    existing_data = []

    if os.path.exists(filename):
        try:
            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:
                existing_data = json.load(f)

            if not isinstance(existing_data, list):
                existing_data = []

        except (
            json.JSONDecodeError,
            OSError
        ):
            existing_data = []

    existing_urls = {
        item.get("url")
        for item in existing_data
        if isinstance(item, dict)
    }

    new_data = []

    for item in data:

        if item.get("url") in existing_urls:
            continue

        new_data.append(item)


    merged_data = (
        new_data +
        existing_data
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            merged_data,
            f,
            ensure_ascii=False,
            indent=2
        )

        f.write("\n")


    print(
        f"Saved: {filename} "
        f"(new: {len(new_data)}, "
        f"total: {len(merged_data)})"
    )


if __name__ == "__main__":
    fetch_ipa()
