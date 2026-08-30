import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


BASE_URL = "https://csrc.nist.gov/publications/search"
OUTPUT_DIR = "data"

TARGET_DATE = None #本番
# TARGET_DATE = "2026-08-21" #TEST


def fetch_nist():

    if TARGET_DATE:
        target_date = TARGET_DATE
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    response = requests.get(
        BASE_URL,
        headers={
            "User-Agent": "SecurityWatch/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    documents = []
    urls = set()

    for link in soup.select('a[href*="/pubs/"]'):

        title = link.get_text(
            " ",
            strip=True
        )

        url = link.get(
            "href",
            ""
        )

        if not title or not url:
            continue

        if url.startswith("/"):
            url = "https://csrc.nist.gov" + url

        if url in urls:
            continue

        row = link.find_parent("tr")

        if not row:
            continue

        row_text = row.get_text(
            " ",
            strip=True
        )

        urls.add(url)

        documents.append({
            "title": title,
            "url": url,
            "row_text": row_text
        })

    print(
        f"NIST: {len(documents)}件の文書を確認"
    )

    articles = []

    for document in documents:

        row_text = document["row_text"]

        date_match = re.search(
            r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
            row_text
        )

        if not date_match:
            continue

        try:

            document_date = datetime.strptime(
                date_match.group(1),
                "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

        except ValueError:

            continue

        if document_date != target_date:
            continue

        identifier = None
        status = None

        identifier_match = re.search(
            r"\b("
            r"SP\s+\d+(?:-\d+)?"
            r"(?:\s+Rev\.\s*\d+)?"
            r"|IR\s+\d+"
            r"|FIPS\s+\d+"
            r"|CSWP\s+\d+(?:[A-Za-z0-9]+)?"
            r")\b",
            row_text,
            re.IGNORECASE
        )

        if identifier_match:

            identifier = identifier_match.group(1)

            identifier = re.sub(
                r"\s+",
                " ",
                identifier
            ).strip()

        if re.search(
            r"\bFinal\b",
            row_text,
            re.IGNORECASE
        ):
            status = "Final"

        elif re.search(
            r"\b(?:Initial Public Draft|Initial Working Draft|Public Draft|Working Draft|Draft)\b",
            row_text,
            re.IGNORECASE
        ):
            status = "Draft"

        if identifier and status:

            identifier = (
                f"{identifier} ({status})"
            )

        elif status:

            identifier = status

        articles.append({
            "source": "海外",
            "date": document_date,
            "time": None,
            "organization": "NIST",
            "identifier": identifier,
            "title": document["title"],
            "url": document["url"]
        })

    print(
        f"NIST: {len(articles)}件取得"
    )

    if not articles:

        print(
            "NIST: 対象日の新着記事なし"
        )

        return

    output_file = os.path.join(
        OUTPUT_DIR,
        f"feed_{target_date.replace('-', '')}.json"
    )

    existing = []

    if os.path.exists(output_file):

        try:

            with open(
                output_file,
                "r",
                encoding="utf-8"
            ) as f:

                existing = json.load(f)

        except Exception:

            existing = []

    existing_urls = {
        item.get("url")
        for item in existing
    }

    new_articles = []

    for article in articles:

        if article["url"] in existing_urls:
            continue

        existing_urls.add(
            article["url"]
        )

        new_articles.append(
            article
        )

    if not new_articles:

        print(
            "NIST: 新しい記事なし"
        )

        return

    existing.extend(
        new_articles
    )

    existing.sort(
        key=lambda x: (
            x.get("date", ""),
            x.get("time") or ""
        ),
        reverse=True
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            existing,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"NIST: {len(new_articles)}件追加"
    )

    print(
        f"保存先: {output_file}"
    )


if __name__ == "__main__":
    fetch_nist()
