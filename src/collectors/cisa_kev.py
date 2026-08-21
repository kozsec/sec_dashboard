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

    # TEST ot not
    if TEST_DATE:
        target_date = TEST_DATE
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    vulnerabilities = []

    for item in data.get("vulnerabilities", []):

        if item.get("dateAdded") != target_date:
            continue

        vulnerability = {
            "source": "CISA KEV",
            "date": item.get("dateAdded"),
            "time": None,
            "organization": item.get("vendorProject"),
            "product": item.get("product"),
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

    # Output(feed)
    save_json(vulnerabilities)

    # Output(vuln)
    save_vulnerabilities_json(
        vulnerabilities
    )

    return vulnerabilities


# -- Save(Feed)
def save_json(data):

    if not data:
        print("No new CISA KEV vulnerabilities.")
        return

    date_str = data[0]["date"].replace("-", "")

    filename = (
        f"data/feed_{date_str}.json"
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

            try:
                existing_data = json.load(f)

            except json.JSONDecodeError:
                existing_data = []


    existing_urls = {
        item.get("url")
        for item in existing_data
        if isinstance(item, dict)
        and item.get("url")
    }


    new_data = [
        item
        for item in data
        if item.get("url")
        and item["url"] not in existing_urls
    ]

    combined_data = (
        new_data +
        existing_data
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            combined_data,
            f,
            ensure_ascii=False,
            indent=2
        )

        f.write("\n")


    print(
        f"New data: {len(new_data)}"
    )

    print(
        f"Total vulnerabilities: "
        f"{len(combined_data)}"
    )

    print(
        f"Saved: {filename}"
    )


# -- Save(vuln)
def save_vulnerabilities_json(data):

    if not data:
        print(
            "No new CISA KEV vulnerabilities "
            "for vulnerabilities.json."
        )
        return

    filename = "data/vulnerabilities.json"

    os.makedirs(
        "data",
        exist_ok=True
    )


    existing_records = []

    if os.path.exists(filename):

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            try:
                existing_records = json.load(f)

            except json.JSONDecodeError:
                existing_records = []


    existing_by_cve = {
        item.get("cve"): item
        for item in existing_records
        if isinstance(item, dict)
        and item.get("cve")
    }


    new_records = []


    for item in data:

        date_added = item.get("date")

        if date_added:

            published = datetime.strptime(
                date_added,
                "%Y-%m-%d"
            ).strftime("%Y/%m/%d")

        else:

            published = None


        cve = item.get("identifier")

        if cve in existing_by_cve:

            record = existing_by_cve[cve]

            record["kev"] = "あり"

            if not record.get("published"):
                record["published"] = published

            if not record.get("last_update"):
                record["last_update"] = published

            continue

        record = {
            "cve": cve,
            "company": item.get("organization"),
            "product": None,
            "title": item.get("title"),
            "kev": "あり",
            "epss_current": None,
            "cvss": None,
            "cvss_vector": None,
            "published": published,
            "last_update": published
        }

        new_records.append(record)

    combined_records = (
        new_records +
        existing_records
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            combined_records,
            f,
            ensure_ascii=False,
            indent=2
        )

        f.write("\n")


    print(
        f"New vulnerabilities: "
        f"{len(new_records)}"
    )

    print(
        f"Total vulnerabilities: "
        f"{len(combined_records)}"
    )

    print(
        f"Saved: {filename}"
    )


# -- Main
if __name__ == "__main__":

    vulnerabilities = fetch_cisa_kev()
