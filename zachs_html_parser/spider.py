import re

import requests

from zachs_html_parser import easy

import time

def allow_disallow_sites(link):
    base_url = easy.base_url(link)
    robotstxt = requests.get(base_url + '/robots.txt').text
    pattern = re.compile(r'(User-agent: \*\s)((Allow: .+?\s|Disallow: .+?\s)+)', re.MULTILINE)
    allow_disallow = pattern.findall(robotstxt)
    fixed_regex = ''
    for x in allow_disallow[0]:
        fixed_regex += x
    allow_disallow = fixed_regex.split('\n')
    allow_disallow = allow_disallow[1:-1]
    if 'Allow' in fixed_regex:
        allow_disallow_list = ['allow']
        for x in allow_disallow:
            if x[0] == 'A':
                allowed_url = base_url + x[7:]
                allow_disallow_list.append(allowed_url)
    else:
        allow_disallow_list = ['disallow']
        for x in allow_disallow:
            allowed_url = base_url + x[10:]
            allow_disallow_list.append(allowed_url)
    return allow_disallow_list

def find_crawl_delay(robotstxt_site):
    txt = requests.get(robotstxt_site).text
    pattern = re.compile(r'Crawl-delay: \d(\.\d+)?', re.MULTILINE)
    matches = pattern.findall(txt)
    if len(matches) > 0:
        return matches[0]
    else:
        return 0

# The intention of this is to get all the sites in a link (and the links in those) but also automatically check if it obeys robots.txt
# It is unclear if it works but it seems to. If you want to test it, go ahead. I would appreciate it if you tweeted me the results at https://twitter.com/zperk13
def scraper(link, generations=2, print_generation=False, print_crawl_delay=False):
    crawl_delay = find_crawl_delay(easy.base_url(link)+'/robots.txt')
    if print_crawl_delay:
        print('Crawl Delay:', crawl_delay)
    time.sleep(crawl_delay)
    allow_disallow_list = allow_disallow_sites(link)
    def allow():
        allowed_sites = allow_disallow_list[1:]
        def check_if_allowed(url):
            allowed_url = False
            url_len = len(url)
            for site in allowed_sites:
                site_len = len(site)
                if site_len <= url_len:
                    if url[:site_len] == site:
                        allowed_url = True
            return allowed_url
        ok_sites = []
        to_check_sites = [link]
        checked_sites = []
        for generation in range(generations):
            if print_generation:
                print(f'Generation: {generation+1}/{generations}')
            next_to_check_sites = []
            for site in to_check_sites:
                if check_if_allowed(site):
                    ok_sites.append(site)
                    for a in easy.all_links(link):
                        time.sleep(crawl_delay)
                        if a not in checked_sites:
                            next_to_check_sites.append(a)
                checked_sites.append(site)
            to_check_sites = next_to_check_sites
        return ok_sites


    def disallow():
        disallowed_sites = allow_disallow_list[1:]

        def check_if_disallowed(url):
            disallowed_url = False
            url_len = len(url)
            for site in disallowed_sites:
                site_len = len(site)
                if site_len <= url_len:
                    if url[:site_len] == site:
                        base_url_len = len(link)
                        if base_url_len <= url_len:
                            if url[:base_url_len] == base_url_len:
                                disallowed_url = True
            return disallowed_url

        ok_sites = []
        to_check_sites = [link]
        checked_sites = []
        for generation in range(generations):
            if print_generation:
                print(f'Generation: {generation+1}/{generations}')
            next_to_check_sites = []
            for site in to_check_sites:
                if not check_if_disallowed(site):
                    ok_sites.append(site)
                    for a in easy.all_links(link):
                        time.sleep(crawl_delay)
                        if a not in checked_sites:
                            next_to_check_sites.append(a)
                checked_sites.append(site)
            to_check_sites = next_to_check_sites
        return ok_sites
    if allow_disallow_list[0] == 'allow':
        return allow()
    else:
        return disallow()
