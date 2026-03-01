import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def check_site(site, username):
    url = site["url"].format(username)

    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            status = "FOUND"
        else:
            status = "NOT FOUND"
    except:
        status = "ERROR"

    return {
        "site": site["name"],
        "url": url,
        "status": status
    }


def scan_sites(username, sites):

    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(check_site, site, username) for site in sites]

        for future in as_completed(futures):
            yield future.result()
