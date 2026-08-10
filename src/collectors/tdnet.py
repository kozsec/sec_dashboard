import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TDNET_URL = "https://www.release.tdnet.info/inbs/I_main_00.html"


def fetch_tdnet():
    response = requests.get(
        TDNET_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    print(f"TDnet status: {response.status_code}")
    print(f"Page title: {soup.title.get_text(strip=True)}")

    # iframeのURLゲット
    list_iframe = None

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")

        if src and "I_list_001_" in src:
            list_iframe = urljoin(TDNET_URL, src)
            break

    if not list_iframe:
        raise RuntimeError("TDnet disclosure list iframe was not found.")

    print(f"Disclosure list: {list_iframe}")

    # 開示データをゲット
    list_response = requests.get(
        list_iframe,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    list_response.raise_for_status()
    list_response.encoding = "utf-8"

    list_soup = BeautifulSoup(
        list_response.text,
        "html.parser"
    )

    print(f"Disclosure page status: {list_response.status_code}")

    tables = list_soup.find_all("table")

    print(f"Found {len(tables)} table(s)")

    # データを構造化
    disclosures = []

    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")

            if len(cells) < 4:
                continue

            texts = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            time = texts[0]
            code = texts[1]
            company = texts[2]
            title = texts[3]

            if not re.fullmatch(r"\d{2}:\d{2}", time):
                continue

            if not code:
                continue

            link = row.find("a", href=True)

            url = None

            if link:
                url = urljoin(
                    list_iframe,
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

    unique_disclosures = []
    seen = set()

    for disclosure in disclosures:
        key = (
            disclosure["time"],
            disclosure["code"],
            disclosure["title"],
            disclosure["url"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_disclosures.append(disclosure)

    print(f"Structured disclosures: {len(unique_disclosures)}")

    for disclosure in unique_disclosures[:10]:
        print(disclosure)


if __name__ == "__main__":
    fetch_tdnet()
