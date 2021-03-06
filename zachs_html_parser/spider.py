import re
import time

import requests

from zachs_html_parser import easy


def allow_disallow_sites(link):
    base_url = easy.base_url(link)
    robotstxt = requests.get(base_url + '/robots.txt', timeout=10).text
    pattern = re.compile(r'(User-agent: \*\s)((Allow: .+?\s|Disallow: .+?\s)+)', re.MULTILINE)
    allow_disallow = pattern.findall(robotstxt)
    if len(allow_disallow) == 0:
        if 'User-agent: *' in robotstxt or len(robotstxt) < 2:
            return ['disallow', '/no_disallow_this_will_never_be_in_an_url']
        raise Exception("No 'User-agent: *' info detected")
    fixed_regex = ''
    for x in allow_disallow[0]:
        fixed_regex += x
    allow_disallow = fixed_regex.split('\n')
    allow_disallow = allow_disallow[1:-1]
    if 'Allow' in fixed_regex:
        allow_disallow_list = ['allow']
        for x in allow_disallow:
            if x[0] == 'A':
                if not ('Disallow' in allow_disallow and x == 'Allow: /'):
                    allowed_url = base_url + x[7:]
                    allow_disallow_list.append(allowed_url)
    else:
        allow_disallow_list = ['disallow']
        for x in allow_disallow:
            allowed_url = base_url + x[10:]
            allow_disallow_list.append(allowed_url)
    return allow_disallow_list


def find_crawl_delay(robotstxt_site):
    txt = requests.get(robotstxt_site, timeout=10).text
    pattern = re.compile(r'(Crawl-delay: \d)(\.\d+)?', re.MULTILINE)
    matches = pattern.findall(txt)
    if len(matches) > 0:
        matches = matches[0]
    else:
        return 0
    if len(matches) > 1:
        crawl_delay = float(matches[0][-1] + matches[1])
    else:
        crawl_delay = int(matches[0][-1])
    return crawl_delay


# The intention of this is to get all the sites in a link (and the links in those) but also automatically check if it obeys robots.txt
# It is unclear if it works but it seems to. If you want to test it, go ahead. I would appreciate it if you tweeted me the results at https://twitter.com/zperk13
# Return a dictionary. dictionary{'pages'} returns a list of pages on the site that are ok to check according to the robots.txt file,
# dictionary{'external_pages'} returns a list of pages from external sites (they are not checked for robots.txt and will need to be run with this function)
def scraper(link, generations=2, print_generation=False, print_crawl_delay=False, debug=False):
    robotstxt_url = easy.base_url(link) + '/robots.txt'
    if debug:
        print('robots.txt url:', robotstxt_url)
    crawl_delay = find_crawl_delay(robotstxt_url)
    if print_crawl_delay or debug:
        print('Crawl Delay:', crawl_delay)
    time.sleep(crawl_delay)
    allow_disallow_list = allow_disallow_sites(link)
    if debug:
        print('DEBUG: allow_disallow_list', allow_disallow_list)

    def allow():
        allowed_sites = allow_disallow_list[1:]
        external_sites = []

        def check_if_allowed(url):
            allowed_url = False
            url_len = len(url)
            if easy.base_url(url) != easy.base_url(link):
                if url not in external_sites:
                    external_sites.append(url)
                if debug:
                    print(f'DEBUG: DETERMINED THAT {url} IS OUT OF SITE, ADDING TO external_sites')
                return False
            for site in allowed_sites:
                site_len = len(site)
                if site_len <= url_len:
                    if url[:site_len] == site:
                        allowed_url = True
            if debug:
                print(f'DEBUG: DETERMINED THAT {url} ALLOWED STATUS IS {allowed_url}')
            return allowed_url

        ok_sites = []
        to_check_sites = [link]
        checked_sites = []
        for generation in range(generations):
            if print_generation or debug:
                print(f'Generation: {generation + 1}/{generations}. Checking {len(to_check_sites)} sites')
            next_to_check_sites = []
            for site in to_check_sites:
                if debug:
                    print(f'DEBUG: CHECKING {site}')
                if check_if_allowed(site):
                    ok_sites.append(site)
                    for a in easy.all_links(link):
                        time.sleep(crawl_delay)
                        if a not in checked_sites and a not in next_to_check_sites and a not in to_check_sites:
                            next_to_check_sites.append(a)
                            if debug:
                                print(f'DEBUG: ADDED {a} TO next_to_check_sites')
                checked_sites.append(site)
                if debug:
                    print(f'DEBUG: ADDED {site} TO checked_sites')

            to_check_sites = next_to_check_sites
        return {'pages': ok_sites, 'external_pages': external_sites}

    def disallow():
        disallowed_sites = allow_disallow_list[1:]
        external_sites = []

        def check_if_disallowed(url):
            disallowed_url = False
            url_len = len(url)
            if easy.base_url(url) != easy.base_url(link):
                if url not in external_sites:
                    external_sites.append(url)
                if debug:
                    print(f'DEBUG: DETERMINED THAT {url} IS OUT OF SITE')
                return True
            for site in disallowed_sites:
                site_len = len(site)
                if site_len <= url_len:
                    if url[:site_len] == site:
                        disallowed_url = True
            if debug:
                print(f'DEBUG: DETERMINED THAT {url} DISALLOWED STATUS IS {disallowed_url}')
            return disallowed_url

        ok_sites = []
        to_check_sites = [link]
        checked_sites = []
        for generation in range(generations):
            if print_generation or debug:
                print(f'Generation: {generation + 1}/{generations}')
            next_to_check_sites = []
            for site in to_check_sites:
                if debug:
                    print(f'DEBUG: CHECKING {site}')
                if not check_if_disallowed(site):
                    ok_sites.append(site)
                    for a in easy.all_links(link):
                        time.sleep(crawl_delay)
                        if a not in checked_sites and a not in next_to_check_sites and a not in to_check_sites:
                            next_to_check_sites.append(a)
                            if debug:
                                print(f'DEBUG: ADDED {a} TO next_to_check_sites')
                checked_sites.append(site)
                if debug:
                    print(f'DEBUG: ADDED {site} TO checked_sites')
            to_check_sites = next_to_check_sites
        return {'pages': ok_sites, 'external_pages': external_sites}

    if allow_disallow_list[0] == 'allow':
        if debug:
            print('DEBUG: USING ALLOW METHOD')
        return allow()
    else:
        if debug:
            print('DEBUG: USING DISALLOW METHOD')
        return disallow()
