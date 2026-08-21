import json
import time
from pathlib import Path
from datetime import datetime
import requests

BASE_DIR = Path(__file__).resolve().parent

JSON_FILE = (
    BASE_DIR
    / "data"
    / "vulnerabilities.json"
)
EPSS_URL = ("https://api.first.org/data/v1/epss")
NVD_URL = ("https://services.nvd.nist.gov/rest/json/cves/2.0")
HEADERS = {"User-Agent": "SecurityWatch/1.0"}
REQUEST_TIMEOUT = 30
NVD_BATCH_SIZE = 100
EPSS_BATCH_SIZE = 100


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

        return json.load(f)

def chunks(items, size):

    for i in range(
        0,
        len(items),
        size
    ):

        yield items[
            i:i + size
        ]

def get_epss(cves):

    epss_map = {}

    batches = list(
        chunks(
            cves,
            EPSS_BATCH_SIZE
        )
    )


    for batch_index, batch in enumerate(
        batches,
        start=1
    ):

        cve_string = ",".join(batch)

        try:

            response = requests.get(
                EPSS_URL,
                params={
                    "cve": cve_string
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

            for result in results:

                cve = result.get(
                    "cve"
                )

                epss = result.get(
                    "epss"
                )

                if (
                    cve
                    and epss is not None
                ):

                    epss_map[cve] = float(
                        epss
                    )

        except requests.RequestException as e:

            print(
                f"  EPSS ERROR: {e}"
            )

    return epss_map

def get_cvss(cves):

    cvss_map = {}

    batches = list(
        chunks(
            cves,
            NVD_BATCH_SIZE
        )
    )

    for batch_index, batch in enumerate(
        batches,
        start=1
    ):

        cve_string = ",".join(batch)

        max_retries = 5

        for attempt in range(
            max_retries
        ):

            try:

                response = requests.get(
                    NVD_URL,
                    params={
                        "cveIds": cve_string,
                        "resultsPerPage": 100
                    },
                    timeout=REQUEST_TIMEOUT,
                    headers=HEADERS
                )

                if response.status_code == 429:

                    wait_seconds = (
                        10 * (attempt + 1)
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

                for vulnerability in vulnerabilities:

                    cve_data = vulnerability.get(
                        "cve",
                        {}
                    )

                    cve_id = cve_data.get(
                        "id"
                    )

                    if not cve_id:
                        continue

                    metrics = cve_data.get(
                        "metrics",
                        {}
                    )

                    score = None
                    vector = None

                    # CVSS v4.0
                    if metrics.get(
                        "cvssMetricV40"
                    ):

                        cvss_data = metrics[
                            "cvssMetricV40"
                        ][0].get(
                            "cvssData",
                            {}
                        )

                        score = cvss_data.get(
                            "baseScore"
                        )

                        vector = cvss_data.get(
                            "vectorString"
                        )

                    # CVSS v3.1
                    elif metrics.get(
                        "cvssMetricV31"
                    ):

                        cvss_data = metrics[
                            "cvssMetricV31"
                        ][0].get(
                            "cvssData",
                            {}
                        )

                        score = cvss_data.get(
                            "baseScore"
                        )

                        vector = cvss_data.get(
                            "vectorString"
                        )

                    # CVSS v3.0
                    elif metrics.get(
                        "cvssMetricV30"
                    ):

                        cvss_data = metrics[
                            "cvssMetricV30"
                        ][0].get(
                            "cvssData",
                            {}
                        )

                        score = cvss_data.get(
                            "baseScore"
                        )

                        vector = cvss_data.get(
                            "vectorString"
                        )

                    # CVSS v2.0
                    elif metrics.get(
                        "cvssMetricV2"
                    ):

                        cvss_data = metrics[
                            "cvssMetricV2"
                        ][0].get(
                            "cvssData",
                            {}
                        )

                        score = cvss_data.get(
                            "baseScore"
                        )

                        vector = cvss_data.get(
                            "vectorString"
                        )

                    cvss_map[cve_id] = {
                        "cvss": score,
                        "cvss_vector": vector
                    }

                break

            except requests.RequestException as e:

                if (
                    attempt
                    == max_retries - 1
                ):


                    break

                wait_seconds = (
                    5 * (attempt + 1)
                )

                time.sleep(
                    wait_seconds
                )

    return cvss_map


def update_scores(data):

    today = datetime.now().strftime(
        "%Y/%m/%d"
    )

    cves = []

    for item in data:

        cve = item.get(
            "cve"
        )

        if cve:

            cves.append(
                cve
            )

    cves = list(
        dict.fromkeys(
            cves
        )
    )


    if not cves:

        return data, 0

    epss_map = get_epss(
        cves
    )


    cvss_map = get_cvss(
        cves
    )

    updated_count = 0

    for item in data:

        cve = item.get(
            "cve"
        )

        if not cve:
            continue

        changed = False

        if cve in epss_map:

            old_epss = item.get(
                "epss_current"
            )

            new_epss = epss_map[
                cve
            ]

            if old_epss != new_epss:

                item[
                    "epss_current"
                ] = new_epss

                changed = True

        if cve in cvss_map:

            old_cvss = item.get(
                "cvss"
            )

            old_vector = item.get(
                "cvss_vector"
            )

            new_cvss = cvss_map[
                cve
            ][
                "cvss"
            ]

            new_vector = cvss_map[
                cve
            ][
                "cvss_vector"
            ]

            if old_cvss != new_cvss:

                item[
                    "cvss"
                ] = new_cvss

                changed = True

            if old_vector != new_vector:

                item[
                    "cvss_vector"
                ] = new_vector

                changed = True

        if changed:

            old_last_update = item.get(
                "last_update"
            )

            item[
                "last_update"
            ] = today

            updated_count += 1


    return data, updated_count


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

        f.write(
            "\n"
        )


def main():


    data = load_json()

    if not data:

        return

    data, updated_count = (
        update_scores(data)
    )

    save_json(
        data
    )

if __name__ == "__main__":

    main()
