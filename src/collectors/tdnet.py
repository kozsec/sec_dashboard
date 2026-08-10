```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

TDNET_URL = "https://www.release.tdnet.info/inbs/I_main_00.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TEST_DATE = "20260810"

SECURITY_KEYWORDS = [
    "セキュリティ",
    "サイバー攻撃",
    "不正アクセス",
    "ランサムウェア",
    "マルウェア",
    "情報漏えい",
    "情報流出",
    "個人情報",
    "データ流出",
    "不正侵入",
    "フィッシング",
    "脆弱性",
    "インシデント",
    "システム障害",
]


def fetch_tdnet():
    response = requests.get(
        TDNET_URL,
        timeout=30,
        headers=HEADERS
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    print(f"TDnet status: {response.status_code}")
    print(f"Page title: {soup.title.get_text(strip=True)}")

    list_iframe = (
        "https://www.release.tdnet.info/inbs/"
        f"I_list_001_{TEST_DATE}.html"
    )

    print(f"Disclosure list: {list_iframe}")

    disclosures = []
    page = 1

    while True:
        page_url = build_page_url(
            list_iframe,
            page
        )

        print(f"Processing page: {page}")
        print(f"Page URL: {page_url}")

        page_disclosures = fetch_page(page_url)

        print(f"Page disclosures: {len(page_disclosures)}")

        if len(page_disclosures) == 0:
            break

        disclosures.extend(page_disclosures)

        print(f"Total disclosures: {len(disclosures)}")

        page += 1

    print(f"Structured disclosures: {len(disclosures)}")

    security_disclosures = filter_security_disclosures(
        disclosures
    )

    print(
        f"Security-related disclosures: "
        f"{len(security_disclosures)}"
    )

    for disclosure in security_disclosures:
        print(disclosure)

    return security_disclosures


def fetch_page(page_url):
    response = requests.get(
        page_url,
        timeout=30,
        headers=HEADERS
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    print(
        f"Disclosure page status: "
        f"{response.status_code}"
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    disclosures = []

    for row in soup.find_all("tr"):
        cells = row.find_all("td")

        if len(cells) < 4:
            continue

        texts = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        if not is_disclosure_row(texts):
            continue

        time = texts[0]
        code = texts[1]
        company = texts[2]
        title = texts[3]

        link = row.find("a", href=True)

        url = None

        if link:
            url = urljoin(
                page_url,
                link["href"]
            )

        disclosure = {
            "time": time,
            "code": code,
            "company": company,
            "title": title,
            "url": url,
        }

        disclosures.append(disclosure)

    return disclosures


def is_disclosure_row(texts):
    if len(texts) < 4:
        return False

    time = texts[0]
    code = texts[1]
    company = texts[2]
    title = texts[3]

    if len(time) != 5:
        return False

    if time[2] != ":":
        return False

    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return False

    if not code:
        return False

    if not company:
        return False

    if not title:
        return False

    return True


def filter_security_disclosures(disclosures):
    results = []

    for disclosure in disclosures:
        text = (
            disclosure["company"]
            + " "
            + disclosure["title"]
        )

        matched_keywords = [
            keyword
            for keyword in SECURITY_KEYWORDS
            if keyword in text
        ]

        if matched_keywords:
            disclosure["matched_keywords"] = matched_keywords
            results.append(disclosure)

    return results


def build_page_url(first_page_url, page):
    name = first_page_url.split("/")[-1]

    date_part = (
        name
        .replace("I_list_001_", "")
        .replace(".html", "")
    )

    return (
        "https://www.release.tdnet.info/inbs/"
        f"I_list_{page:03d}_{date_part}.html"
    )


if __name__ == "__main__":
    fetch_tdnet()
```
