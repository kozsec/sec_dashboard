from collectors.tdnet import fetch_tdnet
from collectors.kev import fetch_cisa_kev

def main():
    fetch_tdnet()
    fetch_cisa_kev()

if __name__ == "__main__":
    main()
