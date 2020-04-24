# -*- coding: utf-8 -*-
"""This test is vastly inspired by Mike Bayer's article:
http://techspot.zzzeek.org/2012/07/07/the-absolutely-simplest-consistent-hashing-example/
"""

from collections import Counter
from math import sqrt
from random import randint

from uhashring import HashRing


def _pop_std_dev(population):
    mean = sum(population) / len(population)
    return sqrt(sum(pow(n - mean, 2) for n in population) / len(population))


def test_distribution():
    ring = HashRing()

    numnodes = 10
    numhits = 1000
    numvalues = 10000

    for i in range(1, numnodes + 1):
        ring["node{}".format(i)] = {"instance": "node_value{}".format(i)}

    distribution = Counter()
    for i in range(numhits):
        key = str(randint(1, numvalues))
        node = ring[key]
        distribution[node] += 1

    # count of hits matches what is observed
    assert sum(distribution.values()) == numhits

    # usually under 20
    standard_dev = _pop_std_dev(distribution.values())
    assert standard_dev <= 20

    # all nodes should be used
    assert len(distribution) == numnodes

    # just to test getting keys, see that we got the values
    # back and not keys or indexes or whatever.
    assert set(distribution.keys()) == set(
        "node_value{}".format(i) for i in range(1, 1 + numnodes)
    )
