
import json
import time
from pathlib import Path
import requests


# -- Variable
BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = (BASE_DIR / "data" / "vulnerabilities.json")
EPSS_URL = ("https://api.first.org/data/v1/epss")
NVD_URL = ("https://services.nvd.nist.gov/rest/json/cves/2.0")
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 30

# -- Load JSON
def load_json():

    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {JSON_FILE}"
        )

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data


# -- Get EPSS
def get_epss(cve):

    response = requests.get(
        EPSS_URL,
        params={
            "cve": cve
        },
        timeout=REQUEST_TIMEOUT,
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()

    results = data.get(
        "data",
        []
    )

    if not results:
        return None

    return float(results[0]["epss"])


# -- Get CVSS
def get_cvss(cve):

    max_retries = 5

    for attempt in range(max_retries):

        try:

            response = requests.get(
                NVD_URL,
                params={
                    "cveId": cve
                },
                timeout=REQUEST_TIMEOUT,
                headers=HEADERS
            )

            # 429(Too Many Requests)
            if response.status_code == 429:

                wait_seconds = 10 * (
                    attempt + 1
                )

                time.sleep(
                    wait_seconds
                )

                continue

            response.raise_for_status()

            data = response.json()

            vulnerabilities = data.get(
                "vulnerabilities",
                []
            )

            if not vulnerabilities:
                return None, None

            cve_data = vulnerabilities[0].get(
                "cve",
                {}
            )

            metrics = cve_data.get(
                "metrics",
                {}
            )

            # ------------------------------------------------
            # CVSS v3.1
            # ------------------------------------------------

            if metrics.get(
                "cvssMetricV31"
            ):

                cvss_data = metrics[
                    "cvssMetricV31"
                ][0]["cvssData"]

                return (
                    cvss_data.get(
                        "baseScore"
                    ),
                    cvss_data.get(
                        "vectorString"
                    )
                )

            # ------------------------------------------------
            # CVSS v3.0
            # ------------------------------------------------

            if metrics.get(
                "cvssMetricV30"
            ):

                cvss_data = metrics[
                    "cvssMetricV30"
                ][0]["cvssData"]

                return (
                    cvss_data.get(
                        "baseScore"
                    ),
                    cvss_data.get(
                        "vectorString"
                    )
                )

            # ------------------------------------------------
            # CVSS v2
            # ------------------------------------------------

            if metrics.get(
                "cvssMetricV2"
            ):

                cvss_data = metrics[
                    "cvssMetricV2"
                ][0]["cvssData"]

                return (
                    cvss_data.get(
                        "baseScore"
                    ),
                    cvss_data.get(
                        "vectorString"
                    )
                )

            return None, None

        except requests.RequestException as e:

            if attempt == max_retries - 1:

                print(
                    f"  NVD ERROR: {e}"
                )

                return None, None

            wait_seconds = 5 * (
                attempt + 1
            )

            time.sleep(
                wait_seconds
            )

    return None, None


# -- Update JSON
def update_scores(data):

    total = len(data)

    for index, item in enumerate(data, start=1):

        cve = item.get("cve")

        if not cve:
            print(
                f"[{index}/{total}] "
                "CVE not found. Skip."
            )
            continue

        print(
            f"[{index}/{total}] "
            f"{cve}"
        )

        # update EPSS
        try:

            epss = get_epss(cve)

            item["epss_current"] = epss

            print(
                f"  EPSS: {epss}"
            )

        except requests.RequestException as e:

            print(
                f"  EPSS ERROR: {e}"
            )

        # update CVSS

        try:

            cvss, vector = get_cvss(cve)

            item["cvss"] = cvss
            item["cvss_vector"] = vector

            print(
                f"  CVSS: {cvss}"
            )

            print(
                f"  VECTOR: {vector}"
            )

        except requests.RequestException as e:

            print(
                f"  CVSS ERROR: {e}"
            )

        # Avoid rate limit
        time.sleep(0.6)

    return data


# -- Save JSON
def save_json(data):

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

        f.write("\n")

    print(
        f"Saved: {JSON_FILE}"
    )



# Main

def main():

    data = load_json()

    if not data:
        print("No vulnerabilities.")
        return

    data = update_scores(data)

    save_json(data)


if __name__ == "__main__":
    main()