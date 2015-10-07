# -*- coding: utf-8 -*-
"""
"""
import pytest
import types

from collections import Counter
from uhashring import HashRing


@pytest.fixture
def ring():
    ring = HashRing(
        nodes={'node1': 1,
               'node2': 1,
               'node3': 1},
        replicas=4,
        vnodes=40,
        compat=True)
    return ring


@pytest.fixture
def ring_fast():
    ring = HashRing(
        nodes={'node1': 1,
               'node2': 1,
               'node3': 1},
        replicas=4,
        vnodes=40,
        compat=False)
    return ring


def test_ring_size(ring, ring_fast):
    assert ring.size == len(ring.get_nodes()) * 160
    assert ring.size == len(ring._keys)
    assert ring.size == len(ring._ring)
    assert ring.size == len(ring.get_points())

    assert ring_fast.size == len(ring.get_nodes()) * 160
    assert ring_fast.size == len(ring._keys)
    assert ring_fast.size == len(ring._ring)
    assert ring_fast.size == len(ring.get_points())

    assert ring.size == ring_fast.size


def test_consistency(ring):
    coconut_node = ring.get('coconut')
    zoro_node = ring.get('zoro')

    del ring['node3']

    with pytest.raises(KeyError):
        del ring['node3']

    assert coconut_node == ring.get('coconut')
    assert zoro_node != ring.get('zoro')

    ring.add_node('node3', 1)

    assert zoro_node == ring.get('zoro')


def test_aliases(ring):
    assert ring.add_node == ring.__setitem__
    assert ring.get_node_instance == ring.__getitem__
    assert ring.remove_node == ring.__delitem__
    assert ring.continuum == ring.ring


def test_ketama_ring_hashi(ring):
    h = ring.hashi('test')
    assert h == 3446378249 == ring.get_key('test')


def test_faster_ring_hashi(ring_fast):
    h = ring_fast.hashi('test')
    assert h == 12707736894140473154801792860916528374


def test_range(ring):
    r = list(ring.range('test'))
    r.sort()
    c = ring.conf.values()
    c.sort()
    assert r == c

    r = list(ring.range('test', size=2, unique=True))
    assert len(r) == 2

    r = list(ring.range('test', size=2, unique=False))
    assert len(r) == 2

    r = list(ring.range('1800'))  # 1800 is at position 0
    r = list(ring.range('849'))  # 849 is at position -2

    r = list(ring.range('test', size=None, unique=False))
    assert len(r) == ring.size

    l = []
    for node in ring.iterate_nodes('test'):
        l.append(node)
    assert len(l) == 3

    ring_empty = HashRing()
    for node in ring_empty.iterate_nodes('test'):
        assert node is None


def test_conf():
    ring_1 = HashRing({'node1': 1})
    ring_2 = HashRing('node1')
    ring_3 = HashRing(['node1'])
    ring_4 = HashRing({'node1': {'weight': 1}})

    assert ring_1.ring == ring_2.ring == ring_3.ring == ring_4.ring

    with pytest.raises(ValueError):
        HashRing({'node1': 'fail'})

    with pytest.raises(ValueError):
        HashRing(None)


def test_empty_ring():
    ring = HashRing()
    assert ring.get('test') == None


def test_methods_return_types(ring):
    assert isinstance(ring['test'], type(None))
    assert isinstance(ring.get('test'), dict)
    assert isinstance(ring.get_node('test'), str)
    assert isinstance(ring.get_nodes(), list)
    assert isinstance(ring.get_node_hostname('test'), str)
    assert isinstance(ring.get_node_port('test'), type(None))
    assert isinstance(ring.get_node_pos('test'), int)
    assert isinstance(ring.get_node_weight('test'), int)
    assert isinstance(ring.get_points(), list)
    assert isinstance(ring.get_server('test'), tuple)
    assert isinstance(ring.iterate_nodes('test'), types.GeneratorType)
    assert isinstance(ring.range('test'), types.GeneratorType)
    assert isinstance(ring.distribution, Counter)


def test_print_without_error(ring):
    assert ring.print_continuum() == None
    ring = HashRing()
    assert ring.print_continuum() == None
