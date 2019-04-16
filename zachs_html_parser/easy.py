import re

import requests

from zachs_html_parser import tag_finder


def base_url(url):
    base_link_list = re.findall(r'(https://www\.|http://www\.|https://|http://)(.+?(/|$))', url)[0]
    base_link = base_link_list[0] + base_link_list[1][:-1]
    return base_link


def all_links(link, html=''):
    # function needs url to work properly, but you might've already made a request and might not want to do that again
    # so you can give the html, and it wont't request again
    if html=='':
        html = requests.get(link, timeout=5).text
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
