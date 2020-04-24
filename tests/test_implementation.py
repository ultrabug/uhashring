# -*- coding: utf-8 -*-
"""
"""
import sys
import types
from collections import Counter
from uuid import uuid4

import pytest

from uhashring import HashRing

PY3 = sys.version_info >= (3,)


@pytest.fixture
def ring():
    ring = HashRing(nodes={"node1": 1, "node2": 1, "node3": 1}, hash_fn="ketama")
    return ring


@pytest.fixture
def ring_fast():
    ring = HashRing(nodes={"node1": 1, "node2": 1, "node3": 1}, compat=False)
    return ring


def weight_fn(**conf):
    print(conf)
    return int(conf["nodename"][-1])


def test_ring_size(ring, ring_fast):
    assert ring.size == len(ring.get_nodes()) * 160
    assert ring.size == len(ring._keys)
    assert ring.size == len(ring._ring)
    assert ring.size == len(ring.get_points())

    assert ring_fast.size == len(ring_fast.get_nodes()) * 160
    assert ring_fast.size == len(ring_fast._keys)
    assert ring_fast.size == len(ring_fast._ring)
    assert ring_fast.size == len(ring_fast.get_points())

    assert ring.size == ring_fast.size


def test_consistency(ring):
    coconut_node = ring.get("coconut")
    zoro_node = ring.get("zoro")

    del ring["node3"]

    with pytest.raises(KeyError):
        del ring["node3"]

    assert coconut_node == ring.get("coconut")
    assert zoro_node != ring.get("zoro")

    ring.add_node("node3", 1)

    assert zoro_node == ring.get("zoro")


def test_aliases(ring):
    assert ring.add_node == ring.__setitem__
    assert ring.get_node_instance == ring.__getitem__
    assert ring.remove_node == ring.__delitem__
    assert ring.continuum == ring.ring
    assert ring.nodes == ring.conf


def test_ketama_ring_hashi(ring):
    h = ring.hashi("test")
    assert h == 3446378249 == ring.get_key("test")


def test_faster_ring_hashi(ring_fast):
    h = ring_fast.hashi("test")
    assert h == 12707736894140473154801792860916528374


# XXX https://docs.python.org/3/whatsnew/3.0.html#ordering-comparisons
@pytest.mark.skipif(PY3, reason="requires python26, python27")
def test_range(ring):
    r = list(ring.range("test"))
    r.sort()
    c = ring.conf.values()
    c.sort()
    assert r == c

    r = list(ring.range("test", size=2, unique=True))
    assert len(r) == 2

    r = list(ring.range("test", size=2, unique=False))
    assert len(r) == 2

    r = list(ring.range("1800"))  # 1800 is at position 0
    r = list(ring.range("849"))  # 849 is at position -2

    r = list(ring.range("test", size=None, unique=False))
    assert len(r) == ring.size

    n = []
    for node in ring.iterate_nodes("test"):
        n.append(node)
    assert len(n) == 3

    ring_empty = HashRing()
    for node in ring_empty.iterate_nodes("test"):
        assert node is None


def test_conf():
    ring_1 = HashRing({"node1": 1})
    ring_2 = HashRing("node1")
    ring_3 = HashRing(["node1"])
    ring_4 = HashRing({"node1": {"weight": 1}})

    assert ring_1.ring == ring_2.ring == ring_3.ring == ring_4.ring

    with pytest.raises(ValueError):
        HashRing({"node1": "fail"})

    with pytest.raises(ValueError):
        HashRing(None)


def test_empty_ring():
    ring = HashRing()
    assert ring.get("test") is None


def test_methods_return_types(ring):
    assert isinstance(ring["test"], type(None))
    assert isinstance(ring.get("test"), dict)
    assert isinstance(ring.get_instances(), list)
    assert isinstance(ring.get_node("test"), str)
    assert isinstance(ring.get_nodes(), type({}.keys()) if PY3 else list)
    assert isinstance(ring.get_node_hostname("test"), str)
    assert isinstance(ring.get_node_port("test"), type(None))
    assert isinstance(ring.get_node_pos("test"), int)
    assert isinstance(ring.get_node_weight("test"), int)
    assert isinstance(ring.get_points(), list)
    assert isinstance(ring.get_server("test"), tuple)
    assert isinstance(ring.iterate_nodes("test"), types.GeneratorType)
    assert isinstance(ring.range("test"), types.GeneratorType)
    assert isinstance(ring.distribution, Counter)


def test_print_without_error(ring):
    assert ring.print_continuum() is None
    ring = HashRing()
    assert ring.print_continuum() is None


def test_with_non_str_objects(ring):
    uid = uuid4()
    ring.get_node(uid)


def test_weight_fn():
    ring = HashRing(
        nodes={"node1": 1, "node2": 1, "node3": 1},
        replicas=4,
        vnodes=40,
        hash_fn="ketama",
        weight_fn=weight_fn,
    )

    assert ring.distribution["node1"] == 80
    assert ring.distribution["node2"] == 160
    assert ring.distribution["node3"] == 240

    ring.regenerate

    assert ring.distribution["node1"] == 80
    assert ring.distribution["node2"] == 160
    assert ring.distribution["node3"] == 240

    with pytest.raises(TypeError):
        ring = HashRing(
            nodes={"node1": 1, "node2": 1, "node3": 1},
            replicas=4,
            vnodes=40,
            hash_fn="ketama",
            weight_fn=12,
        )

    with pytest.raises(TypeError):
        ring = HashRing(
            nodes={"node1": 1, "node2": 1, "node3": 1},
            replicas=4,
            vnodes=40,
            hash_fn="ketama",
            weight_fn="coconut",
        )


def test_ring_growth_ketama(ring):
    add_ring = HashRing(hash_fn="ketama")
    for nodename in ring.nodes:
        add_ring.add_node(nodename)

    assert ring._nodes == add_ring._nodes
    assert ring.ring == add_ring.ring
    assert ring.distribution == add_ring.distribution


def test_ring_growth_meta(ring_fast):
    add_ring = HashRing(compat=False)
    for nodename in ring_fast.nodes:
        add_ring.add_node(nodename)

    assert ring_fast._nodes == add_ring._nodes
    assert ring_fast.ring == add_ring.ring
    assert ring_fast.distribution == add_ring.distribution


def test_ketama_ring_shrink_collision():
    """
    see issue #6 thanks to @bjhockley
    """
    nodes = ["172.31.1.0", "172.31.1.125", "172.31.1.202"]
    ring = HashRing(nodes, hash_fn="ketama")
    ring.remove_node(nodes[1])
    ring.remove_node(nodes[2])
    ring.remove_node(nodes[0])
    assert ring.ring == {}


def test_hash_fn():
    """
    """

    def hash_fn(k):
        return k + "_hash"

    nodes = ["172.31.1.0", "172.31.1.125", "172.31.1.202"]
    ring = HashRing(nodes, hash_fn=hash_fn)
    assert ring.hashi("coconut") == "coconut_hash"
