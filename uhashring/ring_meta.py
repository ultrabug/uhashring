from collections import Counter
from hashlib import md5


class MetaRing:
    """Implement a tunable consistent hashing ring."""

    def __init__(self, hash_fn):
        """Create a new HashRing.

        :param hash_fn: use this callable function to hash keys.
        """
        self._distribution = Counter()
        self._keys = []
        self._node_points = {}
        self._nodes = {}
        self._ring = {}

        if hash_fn and not hasattr(hash_fn, "__call__"):
            raise TypeError("hash_fn should be a callable function")
        self._hash_fn = hash_fn or (lambda key: int(md5(str(key).encode("utf-8")).hexdigest(), 16))

    def hashi(self, key):
        """Returns an integer derived from the md5 hash of the given key."""
        return self._hash_fn(key)

    def _create_ring(self, nodes):
        """Generate a ketama compatible continuum/ring.

        Idempotent per node: any points previously created for a node are
        dropped before its fresh points are added, so calling this again
        (e.g. to change a node's weight, or via `regenerate()`) never
        double-counts or leaves stale entries behind.
        """
        for node_name, node_conf in nodes:
            old_points = self._node_points.pop(node_name, None)
            if old_points:
                for point in old_points:
                    del self._ring[point]
                self._distribution.pop(node_name, None)

            new_points = []
            for w in range(0, node_conf["vnodes"] * node_conf["weight"]):
                self._distribution[node_name] += 1
                point = self.hashi(f"{node_name}-{w}")
                self._ring[point] = node_name
                new_points.append(point)
            self._node_points[node_name] = new_points
        self._keys = sorted(self._ring.keys())

    def _remove_node(self, node_name):
        """Remove the given node from the continuum/ring.

        :param node_name: the node name.
        """
        try:
            self._nodes.pop(node_name)
            points = self._node_points.pop(node_name)
        except Exception:
            raise KeyError(
                "node '{}' not found, available nodes: {}".format(node_name, self._nodes.keys())
            )
        else:
            self._distribution.pop(node_name)
            for point in points:
                del self._ring[point]
            self._keys = sorted(self._ring.keys())
