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

    soup = BeautifulSoup(response.text, "html.parser")

    print(f"TDnet status: {response.status_code}")
    print(f"Page title: {soup.title.get_text(strip=True)}")

    iframes = soup.find_all("iframe")

    print(f"Found {len(iframes)} iframe(s)")

    for iframe in iframes:
        src = iframe.get("src")
        if src:
            print(f"iframe: {urljoin(TDNET_URL, src)}")


if __name__ == "__main__":
    fetch_tdnet()
