import json
import os
import requests
from datetime import datetime

# -- Variable

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -- Variable for Test
TEST_DATE = None
# TEST_DATE = "2026-08-03"


# -- Get CISA KEV data
def fetch_cisa_kev():

    response = requests.get(
        CISA_KEV_URL,
        timeout=30,
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()

    # TEST?
    if TEST_DATE:
        target_date = TEST_DATE
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    print(f"CISA KEV target date: {target_date}")

    vulnerabilities = []

    for item in data.get("vulnerabilities", []):

        if item.get("dateAdded") != target_date:
            continue

        vulnerability = {
            "source": "CISA KEV",
            "date": item.get("dateAdded"),
            "time": None,
            "organization": item.get("vendorProject"),
            "identifier": item.get("cveID"),
            "title": item.get("vulnerabilityName"),
            "url": (
                "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
                f"?search={item.get('cveID')}"
                "&field_cve="
                "&sort_by=field_date_added"
            )
        }

        vulnerabilities.append(vulnerability)

    print(
        f"CISA KEV vulnerabilities: "
        f"{len(vulnerabilities)}"
    )

    save_json(vulnerabilities)

    return vulnerabilities


# -- Save
def save_json(data):
    if not data:
        print("No new CISA KEV vulnerabilities.")
        return

    date_str = data[0]["date"].replace("-", "")
    filename = (
        f"data/vulnerabilities_{date_str}.json"
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )
    print(f"Saved: {filename}")

# -- Main
if __name__ == "__main__":
    vulnerabilities = fetch_cisa_kev()
