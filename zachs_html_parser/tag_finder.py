import re

from zachs_html_parser import _objects

def a(html):
    pattern = re.compile('(<a.+?</a>|<a\s+?</a>)', re.MULTILINE)
    matches = pattern.findall(html)
    real_matches = []
    for x in matches:
        real_matches.append(_objects._a(x))
    return real_matches
