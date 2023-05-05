from fake_scraper import fake_profile_generator
import requests
from bs4 import BeautifulSoup


def get_wartenummer():
    proxies, headers = fake_profile_generator()
    url = 'https://www.hmt-rostock.de/storages/hmt-rostock/service/wartenummer.php'
    r = requests.get(url,
                     proxies=proxies,
                     headers=headers,
                     timeout=5)
    soup = BeautifulSoup(r.text, 'html.parser')
    wartenummer = soup.body.contents[0]
    return wartenummer.strip()


if __name__ == "__main__":
    get_wartenummer()
    print(get_wartenummer())
