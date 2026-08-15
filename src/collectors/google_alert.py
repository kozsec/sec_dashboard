import os
import json
import base64
import html
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, unquote

import requests
from bs4 import BeautifulSoup

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_QUERY = "from:(googlealerts-noreply@google.com) newer_than:1d"

OUTPUT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
    )
)


def get_access_token():

    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
    client_id = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")

    response = requests.post(
        GMAIL_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )

    if not response.ok:
        print("Gmail OAuth認証失敗")
        print(response.text)
        response.raise_for_status()

    token_data = response.json()

    access_token = token_data.get("access_token")

    return access_token


def gmail_get(url, access_token, params=None):

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        params=params,
        timeout=30,
    )

    if not response.ok:
        print(
            f"responsエラー。コード： {response.status_code}"
        )
        print(response.text)
        response.raise_for_status()

    return response.json()

def decode_body(data):

    if not data:
        return ""

    padding = "=" * (-len(data) % 4)

    try:
        return base64.urlsafe_b64decode(
            data + padding
        ).decode(
            "utf-8",
            errors="replace",
        )
    except Exception:
        return ""


def extract_html_from_payload(payload):

    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/html":
        data = payload.get("body", {}).get("data")

        if data:
            return decode_body(data)

    for part in payload.get("parts", []):
        result = extract_html_from_payload(part)

        if result:
            return result

    return ""


def unwrap_google_url(url):

    url = html.unescape(url)

    try:
        parsed = urlparse(url)

        hostname = parsed.netloc.lower()

        if hostname not in (
            "www.google.com",
            "google.com",
        ):
            return url

        query = parse_qs(parsed.query)

        target = query.get("url")

        if target:
            return unquote(target[0])

    except Exception:
        pass

    return url


def is_google_alert_article_link(href):

    if not href:
        return False

    href = html.unescape(href)

    if "google.com/url?" not in href:
        return False

    excluded = [
        "google.co.jp/alerts",
        "google.com/alerts",
    ]

    return not any(
        x in href
        for x in excluded
    )


def extract_alert_keyword(soup):

    text = soup.get_text(
        "\n",
        strip=True,
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # -- これは、届くアラートメールの冒頭が「設定キーワード、配信頻度」の順で必ず書かれているから、頻度の前はキーワードってこと。
    frequency_keywords = [
        "その都度",
        "1日1回",
        "週1回",
    ]

    for i, line in enumerate(lines):

        for frequency in frequency_keywords:

            if frequency in line and i > 0:

                keyword = lines[i - 1].strip()

                if keyword:
                    return keyword

    return None


def extract_articles(body):

    soup = BeautifulSoup(
        body,
        "html.parser"
    )

    identifier = extract_alert_keyword(
        soup
    )

    articles = []

    url_links = {}

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = html.unescape(
            link.get("href", "")
        )

        if not is_google_alert_article_link(
            href
        ):
            continue

        url = unwrap_google_url(
            href
        )

        if not url.startswith(
            ("http://", "https://")
        ):
            continue

        if url not in url_links:
            url_links[url] = []

        url_links[url].append(link)

    for url, links in url_links.items():

        title_link = max(
            links,
            key=lambda x: len(
                x.get_text(
                    " ",
                    strip=True
                )
            )
        )

        title = title_link.get_text(
            " ",
            strip=True
        )

        if not title:
            continue

        organization = urlparse(url).hostname
        
        if organization:
            organization = organization.removeprefix("www.")

        articles.append(
            {
                "title": title,
                "organization": organization,
                "identifier": identifier,
                "url": url,
            }
        )

    return articles


def get_message_ids(access_token):

    data = gmail_get(
        f"{GMAIL_API_BASE}/messages",
        access_token,
        params={
            "q": GMAIL_QUERY,
            "maxResults": 100,
        },
    )

    messages = data.get(
        "messages",
        [],
    )


    return messages


def get_message(
    access_token,
    message_id,
):

    return gmail_get(
        f"{GMAIL_API_BASE}/messages/{message_id}",
        access_token,
        params={
            "format": "full",
        },
    )


def get_message_date(message):

    internal_date = message.get(
        "internalDate"
    )

    if internal_date:

        dt = datetime.fromtimestamp(
            int(internal_date) / 1000,
            tz=timezone.utc,
        ).astimezone()

        return dt.strftime(
            "%Y-%m-%d"
        )

    return datetime.now().astimezone().strftime(
        "%Y-%m-%d"
    )


def load_json(path):

    if not os.path.exists(path):
        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except json.JSONDecodeError:

        return []


def save_json(path, data):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

        f.write("\n")


def append_articles(
    date_string,
    articles,
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    path = os.path.join(
        OUTPUT_DIR,
        f"other_{date_string.replace('-', '')}.json",
    )

    data = load_json(path)

    existing_urls = {
        item.get("url")
        for item in data
        if isinstance(item, dict)
    }

    added = 0
    skipped = 0

    for article in articles:

        url = article["url"]

        if url in existing_urls:

            skipped += 1

            continue

        record = {
            "source": "Web",
            "date": date_string,
            "time": None,
            "organization": article.get(
                "organization"
            ),
            "identifier": article.get(
                "identifier"
            ),
            "title": article["title"],
            "url": url,
        }

        data.insert(0, record)

        existing_urls.add(url)

        added += 1

    if added > 0:
        save_json(
            path,
            data,
        )

    return added, skipped


def fetch_gmail_alerts():

    access_token = get_access_token()

    messages = get_message_ids(
        access_token
    )

    if not messages:

        return

    total_articles = 0
    total_added = 0
    total_skipped = 0

    for index, message in enumerate(
        messages,
        start=1,
    ):

        message_id = message["id"]

        try:

            message_data = get_message(
                access_token,
                message_id,
            )

            body = extract_html_from_payload(
                message_data.get(
                    "payload",
                    {},
                )
            )

            if not body:

                continue

            articles = extract_articles(
                body
            )

            total_articles += len(
                articles
            )

            if not articles:
                continue

            date_string = get_message_date(
                message_data
            )

            added, skipped = append_articles(
                date_string,
                articles,
            )

            total_added += added
            total_skipped += skipped

        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    fetch_gmail_alerts()
