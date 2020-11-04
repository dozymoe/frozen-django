# pylint:disable=missing-module-docstring,missing-function-docstring
from frozen_django import main

def test_find_next_http_page():
    assert main.find_next_http_page({'a': 1}) is None
