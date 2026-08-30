import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


RSS_FEEDS = {
    "Guidance": "https://www.ncsc.gov.uk/api/1/services/v1/guidance-rss-feed.xml",
    "News": "https://www.ncsc.gov.uk/api/1/services/v1/news-rss-feed.xml",
    "Threat Report": "https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml",
    "Blog": "https://www.ncsc.gov.uk/api/1/services/v1/blog-post-rss-feed.xml",
}

OUTPUT_DIR = "data"

def fetch_rss(url):
    headers = {
        "User-Agent": "SecurityWatch/1.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.content


def parse_date(date_string):
    if not date_string:
        return "", ""

    try:
        dt = parsedate_to_datetime(date_string)

        dt = dt.astimezone()

        return (
            dt.strftime("%Y-%m-%d"),
            dt.strftime("%H:%M")
        )

    except Exception:
        return "", ""




def parse_rss(xml_data, category):
    root = ET.fromstring(xml_data)

    articles = []

    for item in root.findall(".//item"):

        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()

        if not title or not link:
            continue

        date, time = parse_date(pub_date)
        if date != datetime.now().strftime("%Y-%m-%d"):
            continue

        article = {
            "source": "海外",
            "date": date,
            "time": time,
            "organization": "NCSC",
            "identifier": None,
            "title": title,
            "url": link
        }

        articles.append(article)

    return articles


def save_json(articles):

    if not articles:
        print("NCSC: 新しい記事はありません")
        return

    today = datetime.now().strftime("%Y%m%d")

    output_file = os.path.join(
        OUTPUT_DIR,
        f"feed_{today}.json"
    )

    existing = []

    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # URLで重複排除
    existing_urls = {
        item.get("url")
        for item in existing
    }

    new_articles = []

    for article in articles:

        if article["url"] in existing_urls:
            continue

        existing_urls.add(article["url"])
        new_articles.append(article)

    if not new_articles:
        print("NCSC: 新しい記事なし")
        return

    existing.extend(new_articles)

    existing.sort(
        key=lambda x: (
            x.get("date", ""),
            x.get("time", "")
        ),
        reverse=True
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            existing,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"NCSC: {len(new_articles)}件追加")
    print(f"保存先: {output_file}")

def main():

    all_articles = []

    for category, rss_url in RSS_FEEDS.items():

        print(f"NCSC {category}取得中...")

        try:
            xml_data = fetch_rss(rss_url)

            articles = parse_rss(
                xml_data,
                category
            )

            print(f"  {len(articles)}件取得")

            all_articles.extend(articles)

        except Exception as e:
            print(f"  エラー: {e}")

    save_json(all_articles)


if __name__ == "__main__":
    main()
