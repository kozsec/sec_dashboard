import csv
import io
import json
import os
import requests
from urllib.parse import urljoin
from datetime import datetime

NCO_URL = "https://www.cyber.go.jp/news/list/index.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_nco():
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"NCO target date: {today}")

    year = today[:4]

    csv_url = (
        f"https://www.cyber.go.jp/csv/{year}.csv"
    )

    print(f"NCO CSV: {csv_url}")

    response = requests.get(
        csv_url,
        timeout=30,
        headers=HEADERS
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    print(
        f"HTTP status: {response.status_code}"
    )

    print(
        f"CSV size: {len(response.text)} bytes"
    )

    reader = csv.reader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    print(
        f"NCO CSV rows: {len(rows)}"
    )

    if not rows:
        print("NCO CSV is empty.")
        return []

    print(
        f"CSV header: {rows[0]}"
    )

    items = []

    for row in rows[1:]:

        if len(row) < 6:
            continue

        date_raw = row[0].strip()
        name = row[1].strip()
        path = row[2].strip()
        tag = row[4].strip()
        pdf = row[5].strip()

        if not date_raw:
            continue
        try:
            date_obj = datetime.strptime(
                date_raw,
                "%Y/%m/%d"
            )

            date = date_obj.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            print(
                f"Invalid date: {date_raw}"
            )
            continue

        if date != today:
            continue

        if path and path != "#":

            url = urljoin(
                NCO_URL,
                path
            )

        elif pdf and pdf != "#":

            # PDF列:
            # 225KB|/pdf/press/example.pdf;
            #
            # 最初のPDF URLを使用
            url = None

            pdf_parts = pdf.split(";")

            for pdf_part in pdf_parts:

                if "|" not in pdf_part:
                    continue

                _, pdf_path = pdf_part.split(
                    "|",
                    1
                )

                pdf_path = pdf_path.strip()

                if not pdf_path:
                    continue

                url = urljoin(
                    NCO_URL,
                    pdf_path
                )

                break

            if not url:
                url = NCO_URL

        else:

            url = NCO_URL

        if "注意喚起" in tag:
            identifier = "注意喚起"

        elif "報道発表資料" in tag:
            identifier = "報道発表資料"

        else:
            identifier = "新着情報"

        item = {
            "source": "NCO",
            "date": date,
            "time": None,
            "organization": "国家サイバー統括室",
            "identifier": identifier,
            "title": name,
            "url": url
        }

        if item not in items:
            items.append(item)

    print(
        f"NCO updates: {len(items)}"
    )

    save_json(items)

    return items


def save_json(data):

    if not data:
        print("No NCO updates.")
        return

    date_str = data[0]["date"].replace(
        "-",
        ""
    )

    filename = (
        f"data/feed_{date_str}.json"
    )

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

            if not isinstance(
                existing_data,
                list
            ):
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
    fetch_nco()
