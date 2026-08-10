import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

TDNET_URL = "https://www.release.tdnet.info/inbs/I_main_00.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


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

    list_iframe = None

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")

        if src and "I_list_001_" in src:
            list_iframe = urljoin(TDNET_URL, src)
            break

    # テスト用
    list_iframe = "https://www.release.tdnet.info/inbs/I_list_001_20260810.html"
    
    if not list_iframe:
        raise RuntimeError("TDnet disclosure list iframe was not found.")

    print(f"Disclosure list: {list_iframe}")

    first_page = get_page_number(list_iframe)

    disclosures = []

    for page in range(first_page, 9):
        page_url = build_page_url(list_iframe, page)

        print(f"Processing page: {page}")
        print(f"Page URL: {page_url}")

        page_disclosures = fetch_page(page_url)

        print(f"Page disclosures: {len(page_disclosures)}")

        disclosures.extend(page_disclosures)

        print(f"Total disclosures: {len(disclosures)}")

        if len(page_disclosures) == 0:
            break

        if len(disclosures) >= 752:
            break

    disclosures = disclosures[:752]

    print(f"Structured disclosures: {len(disclosures)}")

    for disclosure in disclosures[:10]:
        print(disclosure)

    return disclosures


def fetch_page(page_url):
    response = requests.get(
        page_url,
        timeout=30,
        headers=HEADERS
    )
    response.raise_for_status()
    response.encoding = "utf-8"

    print(f"Disclosure page status: {response.status_code}")

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
        company = texts[2]
        title = texts[3]

        link = row.find("a", href=True)

        url = None

        if link:
            url = urljoin(page_url, link["href"])

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


def get_page_number(url):
    name = url.split("/")[-1]

    if "I_list_001_" not in name:
        raise RuntimeError("Unexpected TDnet list URL.")

    try:
        date_part = name.split("_")[-1].replace(".html", "")
        datetime.strptime(date_part, "%Y%m%d")
    except ValueError:
        raise RuntimeError("Could not determine TDnet date.")

    return 1


def build_page_url(first_page_url, page):
    if page == 1:
        return first_page_url

    name = first_page_url.split("/")[-1]
    date_part = name.replace("I_list_001_", "").replace(".html", "")

    return (
        f"https://www.release.tdnet.info/inbs/"
        f"I_list_00{page}_{date_part}.html"
    )


if __name__ == "__main__":
    fetch_tdnet()
