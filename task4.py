import re
import time
from collections import defaultdict
from urllib.parse import urlparse

import requests
import validators
from structlog import get_logger

url_regexp = re.compile(r"https?://[A-Za-z.-_/0-9]+")
log = get_logger()


def get_hostname(url):
    parsed_uri = urlparse(url)
    hostname = parsed_uri.netloc
    return hostname


def find_links(url):
    if validators.url(url):
        content = requests.get(url).text
        return url, dict(zip(url_regexp.findall(content), [None] * len(url_regexp.findall(content))))


def build(url):
    visited = []  # List for visited nodes.
    queue = []  # Initialize a queue
    visited.append(url)
    queue.append(url)
    url, links = find_links(url)
    urls = defaultdict()
    tree = defaultdict(lambda: {})
    urls[url] = links
    tree[url] = links

    while queue:
        m = queue.pop(0)
        log.info('m          :', M=m)
        # print(m)
        for neighbour in urls[m]:
            log.info('urls[m]          :', urls=urls[m])
            log.info('neighbour          :', neighbour=neighbour)
            if neighbour not in visited:
                visited.append(neighbour)
                if validators.url(neighbour):
                    queue.append(neighbour)
                    if get_hostname(neighbour) == 'uvik.net':
                        url, links = find_links(neighbour)
                        urls[url] = links
                        tree[m][neighbour] = links
                    else:
                        urls[neighbour] = {}
                        tree[m][neighbour] = {}
                    log.info('urls          :', urls=urls)
    print(urls)
    print(tree)


if __name__ == '__main__':
    start_time = time.time()
    build('https://uvik.net/')
    print("--- %s seconds ---" % (time.time() - start_time))
