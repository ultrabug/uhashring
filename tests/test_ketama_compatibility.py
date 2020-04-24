# -*- coding: utf-8 -*-
"""ketama is not released under pypi !
This test is only run on my dev machine and is not really part of the CI.
"""
try:
    import ketama
except Exception:
    ketama = None
from random import randint
from tempfile import NamedTemporaryFile

import pytest

from uhashring import HashRing


@pytest.fixture
def ketama_config_file(request):
    valid_list = NamedTemporaryFile(prefix="py.test_")
    valid_list.write(b"127.0.0.1:11211\t600\n")
    valid_list.write(b"127.0.0.1:11212\t400\n")
    valid_list.flush()

    def fin():
        valid_list.close()
        print("closed valid_list")

    request.addfinalizer(fin)
    return valid_list.name


def test_ketama_hashi():
    if not ketama:
        return

    ring = HashRing()
    assert ring.hashi("test") == ketama.hashi("test")


def test_ketama_compatibility(ketama_config_file):
    if not ketama:
        return

    ring = HashRing(
        nodes={"127.0.0.1:11211": 600, "127.0.0.1:11212": 400},
        replicas=4,
        vnodes=40,
        compat=True,
    )
    continuum = ketama.Continuum(ketama_config_file)

    assert ring.get_points() == continuum.get_points()

    numhits = 1000
    numvalues = 10000
    for i in range(numhits):
        key = str(randint(1, numvalues))
        assert ring.get_server(key) == continuum.get_server(key)
