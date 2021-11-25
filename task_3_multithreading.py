
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
import validators
import time
from structlog import get_logger
# logging.basicConfig(level='INFO')
import concurrent.futures


class SiteMap:
    executor = ThreadPoolExecutor(max_workers=4)
    log = get_logger()
    url_regexp = re.compile(r"https?://[A-Za-z.-_/0-9]+")

    def get_hostname(self, url):
        parsed_uri = urlparse(url)
        hostname = parsed_uri.netloc
        return hostname

    def find_links(self, url):
        if validators.url(url):
            content = requests.get(url).text
            return self.url_regexp.findall(content)

        self.log.warning('invalid url', link=url)
        return

    # def build_tree(self, url, pool, cache=None, root=None):
    #     if root is None:
    #         root = ElementTree.Element("sitemap")
    #     sub_root = ElementTree.SubElement(root, "url", location=url)
    #     cache = cache or set()
    #     cache.add(url)
    #     for link in self.find_links(url):
    #         if validators.url(url):
    #             if self.get_hostname(url) == self.get_hostname(link):
    #                 if link not in cache:
    #                     self.log.info('add new link that wasn\'t at cache', link=link)
    #                     pool.submit(self.build_tree, url=link, pool=pool, cache=cache, root=sub_root)
    #                     # self.build_tree(url=link, cache=cache, root=sub_root)
    #                 elif sub_root.find(f".*[@location='{link}']") is None:
    #                     self.log.info('add link that was already before on other level', link=link)
    #                     # futures.append(sub_root)
    #                     ElementTree.SubElement(sub_root, "url", location=link)
    #             elif sub_root.find(f".*[@location='{link}']") is None:
    #                 self.log.info('add outside link', link=link)
    #                 # futures.append(sub_root)
    #                 ElementTree.SubElement(sub_root, "url", location=link)
    #     # for future in concurrent.futures.as_completed(futures):
    #     #     print(future.result())
    #     return root

    def build_tree(self, url, cache=None, root=None):
        if root is None:
            root = ElementTree.Element("sitemap")
        sub_root = ElementTree.SubElement(root, "url", location=url)
        cache = cache or set()
        cache.add(url)
        # self.log.info('cached links', cache=cache)
        links = self.executor.submit(self.find_links, url)
        lt = set(links.result())
        # print(lt, 'fsdsfsdfvgfdsgsdfds')
        for link in lt:
            if validators.url(url):
                if self.get_hostname(url) == self.get_hostname(link):
                    if link not in cache:
                        self.log.info('add new link that wasn\'t at cache', link=link)
                        self.build_tree(url=link, cache=cache, root=sub_root)
                        # self.build_tree(link, cache, sub_root)
                    elif sub_root.find(f".*[@location='{link}']") is None:
                        self.log.info('add link that was already before on other level', link=link)
                        ElementTree.SubElement(sub_root, "url", location=link)
                elif sub_root.find(f".*[@location='{link}']") is None:
                    self.log.info('add outside link', link=link)
                    ElementTree.SubElement(sub_root, "url", location=link)
        return root


if __name__ == '__main__':
    start_time = time.time()
    site_map = SiteMap()
    data = site_map.build_tree(url="https://uvik.net/")
    tree = ElementTree.ElementTree(data)
    tree.write("filename2.xml")
    print("--- %s seconds ---" % (time.time() - start_time))

