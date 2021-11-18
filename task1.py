import re
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
import validators

url_regexp = re.compile(r"https?://[A-Za-z.-_/0-9]+")


def get_hostname(url):
    parsed_uri = urlparse(url)
    hostname = parsed_uri.netloc
    return hostname


# def check_url_valid(url):
#     valid = validators.url(url)
#     if valid:
#         return True
#     return False


def find_links(url):
    if validators.url(url):
        content = requests.get(url).text
        return url_regexp.findall(content)


def build_tree(url, cache=None, root=None):
    if root is None:
        root = ElementTree.Element("sitemap")
    sub_root = ElementTree.SubElement(root, "url", location=url)
    cache = cache or set()
    cache.add(url)
    for link in find_links(url):
        if validators.url(url):
            if get_hostname(url) == get_hostname(link):
                if link not in cache:
                    build_tree(link, cache, sub_root)
                elif sub_root.find(f".*[@location='{link}']") is None:
                    ElementTree.SubElement(sub_root, "url", location=link)
            elif sub_root.find(f".*[@location='{link}']") is None:
                ElementTree.SubElement(sub_root, "url", location=link)
    return root


if __name__ == '__main__':
    data = build_tree("https://uvik.net/")
    tree = ElementTree.ElementTree(data)
    tree.write("filename.xml")
