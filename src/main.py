from collectors.tdnet import fetch_tdnet
from collectors.cisa_kev import fetch_cisa_kev
from collectors.ipa import fetch_ipa
from collectors.nco import fetch_nco
from collectors.get_ncsc import main as fetch_ncsc
from collectors.get_nist import fetch_nist
from collectors.get_enisa import fetch_enisa
from collectors.update_epss_cvss import main as update_epss_cvss


def main():
    fetch_tdnet()
    fetch_cisa_kev()
    fetch_ipa()
    fetch_nco()
    fetch_ncsc()
    fetch_nist()
    fetch_enisa()
    update_epss_cvss()


if __name__ == "__main__":
    main()
