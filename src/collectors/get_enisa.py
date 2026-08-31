import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json
import os
import re


BASE_URL = "https://www.enisa.europa.eu"
PUBLICATIONS_URL = f"{BASE_URL}/publications"

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    f"enisa_{datetime.now().strftime('%Y%m%d')}.json"
)


def get_publication_type(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url.strip(),
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        label = soup.find(
            string=lambda s: s and "Publication type" in s
        )

        if label:
            parent = label.parent

            text = parent.get_text(" ", strip=True)

            if text != "Publication type":
                return text.replace(
                    "Publication type",
                    "",
                    1
                ).strip()

            next_element = parent.find_next()
            if next_element:
                value = next_element.get_text(
                    " ",
                    strip=True
                )

                if value and value != "Publication type":
                    return value

        return None

    except requests.RequestException as e:
        print(f"Publication type取得失敗: {url}")
        print(e)

    return None


def fetch_enisa():
    print("ENISA Publications取得開始")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        PUBLICATIONS_URL,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    today = datetime.now().strftime("%Y-%m-%d")
#    today = "2026-07-30" #TEST

    for heading in soup.find_all(["h2", "h3"]):
        link = heading.find("a")

        if not link:
            continue

        title = link.get_text(" ", strip=True)
        url = urljoin(BASE_URL,link.get("href", "")).strip()

        # ENISA Publications以外のリンクを除外
        if not url.startswith(BASE_URL):
            continue

        parent = heading.parent

        if not parent:
            continue

        text = parent.get_text(" ", strip=True)

        date = None

        for element in parent.find_all(
            ["time", "span", "div", "p"]
        ):
            text_value = element.get_text(
                " ",
                strip=True
            )

            try:
                parsed = datetime.strptime(
                    text_value,
                    "%d %B, %Y"
                )

                date = parsed.strftime(
                    "%Y-%m-%d"
                )

                break

            except ValueError:
                pass

        if date != today:
            continue

        description = ""

        publication_type = get_publication_type(url)

        if any(
            item["url"] == url
            for item in results
        ):
            continue

        results.append({
            "source": "海外",
            "date": date,
            "time": "Null",
            "organization": "ENISA",
            "identifier": publication_type,
            "title": title,
            "url": url,
        })

    print(f"ENISA取得: {len(results)}件")

    save_results(results)

    return results


def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    existing = []

    if os.path.exists(OUTPUT_FILE):
        try:
            with open(
                OUTPUT_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                existing = json.load(f)

        except (
            json.JSONDecodeError,
            OSError
        ):
            existing = []

    existing_urls = {
        item.get("url")
        for item in existing
    }

    new_items = [
        item
        for item in results
        if item.get("url") not in existing_urls
    ]

    existing.extend(new_items)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            existing,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"ENISA新規追加: {len(new_items)}件")
    print(f"保存先: {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_enisa()
