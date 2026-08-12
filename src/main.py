from collectors.tdnet import fetch_tdnet
from collectors.cisa_kev import fetch_cisa_kev
from collectors.ipa import fetch_ipa

def main():
    fetch_tdnet()
    fetch_cisa_kev()
    fetch_ipa()

if __name__ == "__main__":
    main()