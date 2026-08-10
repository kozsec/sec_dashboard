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
    current_url = list_iframe
    page_number = 1
    disclosures = []

    while current_url:
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
                cells = row.find_all(["td", "th"])

                if not cells:
                    continue

                texts = [
                    cell.get_text(" ", strip=True)
                    for cell in cells
                ]

                if len(texts) < 4:
                    continue

                time = texts[0]
                code = texts[1]
                company = texts[2]
                title = texts[3]

                if not time or ":" not in time:
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

        disclosures.extend(page_disclosures)

        print(f"Page disclosures: {len(page_disclosures)}")
        print(f"Total disclosures: {len(disclosures)}")

        # 次のページのURLをゲット
        next_url = None

        for link in list_soup.find_all("a", href=True):
            text = link.get_text(" ", strip=True)

            if "次" in text:
                next_url = urljoin(
                    current_url,
                    link["href"]
                )
                break

        current_url = next_url
        page_number += 1

    print(f"Structured disclosures: {len(disclosures)}")

    for disclosure in disclosures[:10]:
        print(disclosure)


if __name__ == "__main__":
    fetch_tdnet()
