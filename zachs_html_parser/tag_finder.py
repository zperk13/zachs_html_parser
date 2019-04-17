import re

import requests

from zachs_html_parser import _objects, spider


def a(html):
    pattern = re.compile('(<a.+?</a>|<a\s+?</a>)', re.MULTILINE)
    matches = pattern.findall(html)
    real_matches = []
    for x in matches:
        real_matches.append(_objects._a(x))
    return real_matches

def safe_a(link):
    safe_site = spider.scraper(link, generations=1)
    if len(safe_site) == 1:
        return a(requests.get(link).text)
