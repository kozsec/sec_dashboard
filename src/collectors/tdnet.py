import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime


# -- Test
testflg = False
if testflg == True:
    test_iframe = "https://www.release.tdnet.info/inbs/I_list_001_20260807.html"

# -- Variable
TDNET_URL = "https://www.release.tdnet.info/inbs/I_main_00.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}
SECURITY_KEYWORDS = [
    "セキュリティ",
    "サイバー攻撃",
    "不正アクセス",
    "ランサムウェア",
    "マルウェア",
    "情報漏洩",
    "情報の漏洩",
    "情報漏えい",
    "情報の漏えい",
    "情報流出",
    "個人情報",
    "データ流出",
    "不正侵入",
    "フィッシング",
    "脆弱性",
    "インシデント",
    "システム障害"
]

# -- Get TDnet data
def fetch_tdnet():
    response = requests.get(
        TDNET_URL,
        timeout=30,
        headers=HEADERS
    )
    response.raise_for_status()
    response.encoding = "utf-8"

    # Get iframe URL
    soup = BeautifulSoup(response.text, "html.parser")
    list_iframe = None
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src and "I_list_001_" in src:
            list_iframe = urljoin(TDNET_URL, src)
            break
    
    # == TEST ==
    if testflg == True:
        list_iframe = test_iframe

    if not list_iframe:
        raise RuntimeError(
            "TDnet disclosure list iframe was not found."
        )

    disclosure_date = get_disclosure_date(list_iframe)
    first_page = get_page_number(list_iframe)
    page = first_page
    disclosures = []

    while True:
        page_url = build_page_url(list_iframe,page)

        # Not found
        try:
            page_disclosures = fetch_page(
                page_url,
                disclosure_date
            )
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break
            raise

        if len(page_disclosures) == 0:
            break

        disclosures.extend(page_disclosures)

        page += 1

    # == DEBUG ==
    print(
        f"Total Records: "
        f"{len(disclosures)}"
    )
    # ===========

    return disclosures


def fetch_page(page_url, disclosure_date):
    response = requests.get(
        page_url,
        timeout=30,
        headers=HEADERS
    )
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

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
        if len(code) == 5 and code.endswith("0"):
            code = code[:-1]
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
            "source": "適時開示",
            "date": disclosure_date,
            "time": time,
            "organization": company,
            "identifier": code,
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


def get_page_number(url):
    name = url.split("/")[-1]

    if "I_list_001_" not in name:
        raise RuntimeError(
            "Unexpected TDnet list URL."
        )

    try:
        date_part = (
            name
            .split("_")[-1]
            .replace(".html", "")
        )

        datetime.strptime(
            date_part,
            "%Y%m%d"
        )

    except ValueError:
        raise RuntimeError(
            "Could not determine TDnet date."
        )

    return 1


def get_disclosure_date(url):
    name = url.split("/")[-1]

    date_part = (
        name
        .split("_")[-1]
        .replace(".html", "")
    )

    try:
        date = datetime.strptime(
            date_part,
            "%Y%m%d"
        )

    except ValueError:
        raise RuntimeError(
            "Could not determine disclosure date."
        )

    return date.strftime("%Y-%m-%d")


def build_page_url(first_page_url, page):
    if page == 1:
        return first_page_url

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


def filter_security_disclosures(disclosures):
    results = []

    for disclosure in disclosures:
        text = (
            disclosure["organization"]
            + " "
            + disclosure["title"]
        )

        if any(
            keyword in text
            for keyword in SECURITY_KEYWORDS
        ):
            results.append(disclosure)

    return results


def save_json(data):
    if not data:
        print("No security-related disclosures.")
        return

    date_str = data[0]["date"].replace("-", "")
    filename = (
        f"data/security_disclosures_{date_str}.json"
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    existing_data = []

    if os.path.exists(filename):
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:
            existing_data = json.load(f)

    existing_urls = {
        item["url"]
        for item in existing_data
        if item.get("url")
    }

    new_data = [
        item
        for item in data
        if item.get("url")
        and item["url"] not in existing_urls
    ]

    existing_data.extend(new_data)

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            existing_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"New data: "
        f"{len(new_data)}"
    )
    print(
        f"Total disclosures: "
        f"{len(existing_data)}"
    )
    print(f"Saved: {filename}")



if __name__ == "__main__":
    all_data = fetch_tdnet()

    filtered_data = filter_security_disclosures(
        all_data
    )

    print(
        f"Security-related disclosures: "
        f"{len(filtered_data)}"
    )

    save_json(filtered_data)
