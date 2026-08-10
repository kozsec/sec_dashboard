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

    disclosures = []
    current_url = list_iframe
    page_number = 1

    while current_url:
        # 開示データをゲット
        list_response = requests.get(
            current_url,
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
        print(f"Processing page: {page_number}")

        tables = list_soup.find_all("table")

        page_disclosures = []

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
                        current_url,
                        link["href"]
                    )

                disclosure = {
                    "time": time,
                    "code": code,
                    "company": company,
                    "title": title,
                    "url": url,
                }

                page_disclosures.append(disclosure)

        page_unique = []
        seen = set()

        for disclosure in page_disclosures:
            key = (
                disclosure["time"],
                disclosure["code"],
                disclosure["title"],
                disclosure["url"],
            )

            if key in seen:
                continue

            seen.add(key)
            page_unique.append(disclosure)

        disclosures.extend(page_unique)

        print(f"Page disclosures: {len(page_unique)}")
        print(f"Total disclosures: {len(disclosures)}")

        # 次ページのURLをゲット
        next_url = None
        
        for link in list_soup.find_all("a"):
            text = link.get_text(" ", strip=True)
        
            if "次へ" in text:
                print(f"Next link: {link}")

        current_url = next_url
        page_number += 1

    # 全体の重複を削除
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
