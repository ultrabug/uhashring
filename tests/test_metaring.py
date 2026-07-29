# -*- coding: utf-8 -*-
"""Regression tests for MetaRing stale-vnodes bugs.

MetaRing._create_ring() used to be purely additive: it appended vnodes into
the existing `_ring`/`_distribution` and never dropped a node's previous
points. This produced three observable bugs:

1. Re-adding an existing node (e.g. to change its weight) doubled up its
   old points on top of the new ones, corrupting `_distribution` and
   `ring.size`.
2. Lowering a node's weight then removing it left orphan `_ring` entries
   (created under the old, higher weight) pointing at a node that no
   longer exists, crashing lookups with a KeyError.
3. `HashRing.regenerate()` called `_create_ring` again on top of the
   existing points, doubling every node's count instead of being
   idempotent, and could never reflect a weight decrease.
"""

from collections import Counter

import pytest

from uhashring import HashRing


def test_readd_existing_node_fixes_distribution():
    """Bug 1: re-adding a node with a different weight must not double-count
    its previously created points."""
    hr = HashRing(nodes=["node1", "node2"])
    assert hr.distribution == Counter({"node1": 160, "node2": 160})

    hr.add_node("node1", {"weight": 10})

    assert hr.distribution == Counter({"node1": 1600, "node2": 160})
    assert hr.size == 1760
    assert hr.size == len(hr._keys) == len(hr._ring)


def test_remove_node_after_weight_decrease_leaves_no_orphan_entries():
    """Bug 2: decreasing a node's weight then removing it must not leave
    stale ring entries (created under the old weight) pointing at the
    removed node."""
    hr = HashRing(nodes={"node1": 10, "node2": 1})
    hr.add_node("node1", {"weight": 1})
    hr.remove_node("node1")

    assert "node1" not in hr._nodes
    assert "node1" not in hr.distribution
    assert set(hr._ring.values()) == {"node2"}

    # lookups over a decent spread of keys must succeed and only ever
    # return the still-live node.
    for i in range(1000):
        assert hr.get_node(str(i)) == "node2"


def test_regenerate_is_idempotent():
    """Bug 3: regenerate() must not double the distribution when called
    again with unchanged node configuration."""
    hr = HashRing(nodes=["node1", "node2"])
    before = Counter(hr.distribution)

    hr.regenerate()

    assert hr.distribution == before
    assert hr.distribution == Counter({"node1": 160, "node2": 160})

    hr.regenerate()

    assert hr.distribution == before


def test_regenerate_shrinks_point_count_with_weight_fn():
    """Bug 3: regenerate() must be able to SHRINK a node's point count when
    weight_fn now returns a smaller weight than before -- the exact use
    case documented in the README."""
    weights = {"node1": 10}

    def weight_fn(**conf):
        return weights.get(conf["nodename"], 1)

    hr = HashRing(nodes=["node1", "node2"], weight_fn=weight_fn)
    assert hr.distribution == Counter({"node1": 1600, "node2": 160})

    weights["node1"] = 1
    hr.regenerate()

    assert hr.distribution == Counter({"node1": 160, "node2": 160})
    assert hr.size == 320
    assert hr.size == len(hr._keys) == len(hr._ring)


def test_add_then_remove_node_restores_original_state():
    """Guard: adding a node and then removing it again must return the ring
    to exactly its original state."""
    hr = HashRing(nodes=["node1", "node2"])
    original_ring = dict(hr._ring)
    original_keys = list(hr._keys)
    original_distribution = Counter(hr.distribution)

    hr.add_node("node3", {"weight": 3})
    hr.remove_node("node3")

    assert hr._ring == original_ring
    assert hr._keys == original_keys
    assert hr.distribution == original_distribution


def test_remove_unknown_node_raises_keyerror():
    """Guard: removing a node that was never added must still raise
    KeyError."""
    hr = HashRing(nodes=["node1", "node2"])

    with pytest.raises(KeyError):
        hr.remove_node("does-not-exist")
