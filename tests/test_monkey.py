# -*- coding: utf-8 -*-
"""
"""

from uhashring import HashRing, monkey


def test_patch_memcache():
    """Returns if no memcache.

    NB:
        test key -> 11212
        zzzzzzzzzz key -> 11211
    """
    monkey.patch_memcache()

    import memcache

    mc = memcache.Client(["127.0.0.1:11211", "127.0.0.0:11212"])
    mc.set("zzzzzzzzzz", 1, 2)
    mc.get("zzzzzzzzzz")
    mc.get("test")
    mc.get((0, "zzzzzzzzzz"))

    assert isinstance(mc.uhashring, HashRing)
