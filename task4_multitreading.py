import concurrent.futures
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


def build_tree(url):
    visited = []  # List for visited nodes.
    queue = []  # Initialize a queue
    visited.append(url)
    queue.append(url)
    url, links = find_links(url)
    urls = dict()
    tree = defaultdict(lambda: {})
    urls[url] = links
    tree[url] = links

    while queue:
        m = queue.pop(0)
        log.info('m:', M=m)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            log.info('urls[m]:', urls=urls[m])
            for neighbour in urls[m]:
                if neighbour not in visited:
                    visited.append(neighbour)
                    if validators.url(neighbour):
                        queue.append(neighbour)
                        if get_hostname(neighbour) == get_hostname(url):
                            log.info('neighbour:', neighbour=neighbour)
                            futures.append(executor.submit(find_links, url=neighbour))
                        else:
                            urls[neighbour] = {}
                            tree[m][neighbour] = None
            log.info('urls future:', urls=urls)

            for future in concurrent.futures.as_completed(futures):
                neighbour, links = future.result()
                log.info('neighbour:', neighbour=neighbour)
                log.info('neighbour:', links=links)
                urls[neighbour] = links
                tree[m][neighbour] = links
                log.info('urls:', urls=urls)
    log.info('final tree:', tree=tree)


if __name__ == '__main__':
    start_time = time.time()
    build_tree('https://uvik.net/')
    print("--- %s seconds ---" % (time.time() - start_time))
