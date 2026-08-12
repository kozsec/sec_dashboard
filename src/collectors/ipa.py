import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

IPA_URL = "https://www.ipa.go.jp/news/index.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_ipa():
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

        if "セキュリティ" not in text:
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

        title = text

        title = title.replace(
            "セキュリティ",
            "",
            1
        ).strip()

        vulnerability = {
            "source": "IPA",
            "date": date,
            "time": None,
            "organization": "IPA",
            "identifier": None,
            "title": title,
            "url": url
        }

        if vulnerability not in items:
            items.append(vulnerability)

    print(
        f"IPA security updates: "
        f"{len(items)}"
    )

    save_json(items)

    return items


def extract_date(text):

    import re

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
        print(
            "No IPA security updates."
        )
        return

    date_str = datetime.now().strftime(
        "%Y%m%d"
    )

    filename = (
        f"data/ipa_{date_str}.json"
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Saved: {filename}"
    )


if __name__ == "__main__":
    fetch_ipa()