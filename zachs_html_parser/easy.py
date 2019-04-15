import re

import requests

from zachs_html_parser import tag_finder


def base_url(url):
    base_link_list = re.findall(r'(https://www\.|http://www\.|https://|http://)(.+?\.)([a-zA-Z]{1,13})', url)[0]
    base_link = ''
    for x in base_link_list:
        base_link += x
    return base_link


def all_links(link):
    html = requests.get(link).text
    raw_links = []
    for x in tag_finder.a(html):
        raw_links.append(x.href())
    links = []
    for x in raw_links:
        # making sure it's actually a link
        if len(x) > 1:
            # making sure it's not a link to an id in the page
            if x[0] != '#':
                # Checks if it's a redirect to another page in the website
                if x[0] != '/':
                    # If not append it to the links list
                    links.append(x)
                else:
                    # If so add the base url in front of it then append it to the links list
                    base_link = base_url(link)
                    links.append(base_link + x)
    return links
