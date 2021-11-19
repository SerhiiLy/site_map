import pytest
from task1 import build_tree


def test_url():
    assert build_tree('https://uvik.net/'), 'filename.xml'


if __name__ == '__main__':
    pytest.main()
