from unittest.mock import patch
from xml.etree import ElementTree

import pytest

from task2 import SiteMap


class Resp:
    def __init__(self, text):
        self.text = text


links = [
    Resp("https://uvik.net, https://uvik.net/1, https://uvik.net/2"),
    Resp("https://uvik.net, https://uvik.net/1, https://uvik.net/2, https://google.net"),
    Resp("https://uvik.net, https://uvik.net/1, https://uvik.net/2"),
]


@pytest.mark.parametrize(
    "test_input, expected_result",
    [
        ("https://uvik.net", 'uvik.net'),
        ("https://uvik.net/23", 'uvik.net'),
    ]
)
def test_get_hostname(test_input, expected_result):
    assert SiteMap().get_hostname(test_input) == expected_result


def test_build_tree():
    patch_links = patch('requests.get', side_effect=links)
    with patch_links:
        res = SiteMap().build_tree("https://uvik.net")
        expected = ElementTree.parse("test_tree.xml")
        tree = ElementTree.tostring(res)
        expected_tree = ElementTree.tostring(expected.getroot())
        assert expected_tree == tree
