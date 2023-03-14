from fake_useragent import UserAgent


def fake_profile_generator():
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    while True:
        try:
            ua = UserAgent()
            break
        except:
            continue

    headers = {'User-Agent': ua.random}

    return proxies, headers
