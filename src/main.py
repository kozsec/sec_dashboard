from collectors.tdnet import fetch_tdnet
from collectors.cisa_kev import fetch_cisa_kev
from collectors.ipa import fetch_ipa
from collectors.nco import fetch_nco
from collectors.update_epss_cvss import main as update_epss_cvss
from collectors.get_nist import fetch_nist


def main():
    fetch_tdnet()
    fetch_cisa_kev()
    fetch_ipa()
    fetch_nco()
    fetch_nist()
    update_epss_cvss()


if __name__ == "__main__":
    main()
