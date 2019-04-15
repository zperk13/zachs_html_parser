import re

import requests

from zachs_html_parser import tag_finder


def get_base_url(url):
    base_link_list = re.findall(r'(https://www\.|http://www\.|https://|http://)(.+?\.)([a-zA-Z]{1,13})', url)[0]
    base_link = ''
    for x in base_link_list:
        base_link += x
    return base_link


def find_all_links(link):
    html = requests.get(link).text
    raw_links = []
    for x in tag_finder.a(html):
        raw_links.append(x.href())
    links = []
    for x in raw_links:
        if len(x) > 1:
            if x[0] != '#':
                if x[0] != '/':
                    links.append(x)
                else:
                    base_link = get_base_url(link)
                    links.append(base_link + x)
    return links
