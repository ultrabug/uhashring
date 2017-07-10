# -*- coding: utf-8 -*-

from bisect import bisect, bisect_left, insort
from collections import Counter
from hashlib import md5
from sys import version_info


class HashRing(object):
    """Implement a ketama compatible consistent hashing ring."""

    def __init__(self,
                 nodes=[],
                 replicas=4,
                 vnodes=40,
                 compat=True,
                 weight_fn=None,
                 hash_fn=None):
        """Create a new HashRing.

        :param nodes: nodes used to create the continuum (see doc for format).
        :param replicas: number of replicas per node (=4 if compat).
        :param vnodes: default number of vnodes per node.
        :param compat: use a ketama compatible hash calculation.
        :param weight_fn: use this function to calculate the node's weight.
        :param hash_fn: use this callable function to hash keys.
        """
        self._default_vnodes = vnodes
        self._distribution = Counter()
        self._hash_fn = None
        self._keys = []
        self._nodes = {}
        self._replicas = 4 if compat else replicas
        self._ring = {}

        if hash_fn:
            if not hasattr(hash_fn, '__call__'):
                raise TypeError('hash_fn should be a callable function')
            self._hash_fn = hash_fn
            self._default_vnodes = 160
            self._replicas = 1

        if weight_fn and not hasattr(weight_fn, '__call__'):
            raise TypeError('weight_fn should be a callable function')
        self._weight_fn = weight_fn

        self._configure_hashi(compat)
        self._configure_nodes(nodes)
        self._create_ring()

    def _configure_hashi(self, compat):
        """Use a ketama compatible hash in compatibility mode (default).

        There is a big performance gap in the hash calculation between
        the ketama C binding and its pure python counterpart.

        Python 3 is doing way better than python 2 thanks to its
        native bytes/int representation.

        Quick benchmark, for 1 million generated ketama compatible keys:
            - python_ketama C binding: 0.8427069187164307 ms
            - python 2: 5.462762832641602 ms
            - python 3: 3.570068597793579 ms
            - pypy: 1.6146340370178223 ms

        When using python 2 and ketama compatibility is not important, you
        can get a better hashing speed using the other provided hashing.

        Quick benchmark, for 1 million generated hash keys:
            - python 2: 3.7595579624176025 ms
            - python 3: 3.268343687057495 ms
            - pypy: 1.9193649291992188 ms
        """
        if compat:
            if version_info >= (3, ):
                self._listbytes = lambda x: x
            self.hashi = self._hashi_ketama
        else:
            # backward compatibility code
            if self._hash_fn is None:
                self.hashi = self._hashi_md5
            else:
                self.hashi = self._hashi_user

    def _configure_nodes(self, nodes):
        """Parse and set up the given nodes.

        :param nodes: nodes used to create the continuum (see doc for format).
        """
        if isinstance(nodes, str):
            nodes = [nodes]
        elif not isinstance(nodes, (dict, list)):
            raise ValueError(
                'nodes configuration should be a list or a dict,'
                ' got {}'.format(type(nodes)))

        conf_changed = False
        for node in nodes:
            conf = {
                'hostname': node,
                'instance': None,
                'nodename': node,
                'port': None,
                'vnodes': self._default_vnodes,
                'weight': 1
            }
            current_conf = self._nodes.get(node, {})
            nodename = node
            # new node, trigger a ring update
            if not current_conf:
                conf_changed = True
            # complex config
            if isinstance(nodes, dict):
                node_conf = nodes[node]
                if isinstance(node_conf, int):
                    conf['weight'] = node_conf
                elif isinstance(node_conf, dict):
                    for k, v in node_conf.items():
                        if k in conf:
                            conf[k] = v
                            # changing those config trigger a ring update
                            if k in ['nodename', 'vnodes', 'weight']:
                                if current_conf.get(k) != v:
                                    conf_changed = True
                else:
                    raise ValueError(
                        'node configuration should be a dict or an int,'
                        ' got {}'.format(type(node_conf)))
            if self._weight_fn:
                conf['weight'] = self._weight_fn(**conf)
            # changing the weight of a node trigger a ring update
            if current_conf.get('weight') != conf['weight']:
                    conf_changed = True
            self._nodes[nodename] = conf
        return conf_changed

    def _create_ring(self):
        """Generate a ketama compatible continuum/ring.
        """
        _weight_sum = 0
        for node_conf in self._nodes.values():
            _weight_sum += node_conf['weight']
        self._weight_sum = _weight_sum

        _distribution = Counter()
        _keys = []
        _ring = {}
        for nodename in self._nodes:
            for h in self._hashi_weight_generator(nodename):
                _ring[h] = nodename
                insort(_keys, h)
                _distribution[nodename] += 1
        self._distribution = _distribution
        self._keys = _keys
        self._ring = _ring

    regenerate = _create_ring

    def _get(self, key, what):
        """Generic getter magic method.

        The node with the nearest but not less hash value is returned.

        :param key: the key to look for.
        :param what: the information to look for in, allowed values:
            - instance (default): associated node instance
            - nodename: node name
            - pos: index of the given key in the ring
            - tuple: ketama compatible (pos, name) tuple
            - weight: node weight
        """
        if not self._ring:
            return None

        pos = self._get_pos(key)
        if what == 'pos':
            return pos

        nodename = self._ring[self._keys[pos]]
        if what in ['hostname', 'instance', 'port', 'weight']:
            return self._nodes[nodename][what]
        elif what == 'dict':
            return self._nodes[nodename]
        elif what == 'nodename':
            return nodename
        elif what == 'tuple':
            return (self._keys[pos], nodename)

    def _get_pos(self, key):
        """Get the index of the given key in the sorted key list.

        We return the position with the nearest hash based on
        the provided key unless we reach the end of the continuum/ring
        in which case we return the 0 (beginning) index position.

        :param key: the key to hash and look for.
        """
        p = bisect(self._keys, self.hashi(key))
        if p == len(self._keys):
            return 0
        else:
            return p

    def _hashi_md5(self, key, replica=None):
        """Returns an integer hash from the given key.
        """
        if replica:
            key = '%s:%s' % (key, replica)
        return int(md5(str(key).encode('utf-8')).hexdigest(), 16)

    def _hashi_ketama(self, key, replica=0):
        """Returns a ketama compatible hash from the given key.
        """
        dh = self._listbytes(md5(str(key).encode('utf-8')).digest())
        rd = replica * 4
        return (
            (dh[3 + rd] << 24) | (dh[2 + rd] << 16) |
            (dh[1 + rd] << 8) | dh[0 + rd])

    def _hashi_user(self, key, replica=0):
        """Returns an integer hash from the given key using the function
        defined by the user.
        """
        return self._hash_fn(key)

    def _hashi_weight_generator(self, nodename):
        """Calculate the weight factor of the given node and
        yield its hash key for every configured replica.

        :param nodename: the node name.
        """
        ks = (self._nodes[nodename]['vnodes'] * len(self._nodes) *
              self._nodes[nodename]['weight']) // self._weight_sum
        for w in range(0, ks):
            w_nodename = '%s-%s' % (nodename, w)
            for i in range(0, self._replicas):
                yield self.hashi(w_nodename, replica=i)

    @staticmethod
    def _listbytes(data):
        """Python 2 compatible int iterator from str.

        :param data: the string to int iterate upon.
        """
        return map(ord, data)

    def _remove_node(self, nodename):
        """Remove the given node from the continuum/ring.

        :param nodename: the node name.
        """
        if nodename not in self._nodes:
            raise KeyError('node \'{}\' not found, available nodes: {}'.format(
                nodename, self._nodes.keys()))

        for h in self._hashi_weight_generator(nodename):
            del self._ring[h]
            index = bisect_left(self._keys, h)
            del self._keys[index]
        self._distribution.pop(nodename)
        self._weight_sum -= self._nodes[nodename]['weight']
        self._nodes.pop(nodename)

    def __delitem__(self, nodename):
        """Remove the given node.

        :param nodename: the node name.
        """
        self._remove_node(nodename)

    remove_node = __delitem__

    def __getitem__(self, key):
        """Returns the instance of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'instance')

    get_node_instance = __getitem__

    def __setitem__(self, nodename, conf={'weight': 1}):
        """Add the given node with its associated configuration.

        :param nodename: the node name.
        :param conf: the node configuration.
        """
        if self._configure_nodes({nodename: conf}):
            self._create_ring()

    add_node = __setitem__

    @property
    def conf(self):
        return self._nodes

    nodes = conf

    @property
    def distribution(self):
        return self._distribution

    @property
    def ring(self):
        return self._ring

    continuum = ring

    @property
    def size(self):
        return len(self._ring)

    def get(self, key):
        """Returns the node object dict matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'dict')

    def get_instances(self):
        """Returns a list of the instances of all the configured nodes.
        """
        return [c.get('instance') for c in self._nodes.values()
                if c.get('instance')]

    def get_key(self, key):
        """Alias of ketama hashi method, returns the hash of the given key.

        This method is present for hash_ring compatibility.

        :param key: the key to look for.
        """
        return self.hashi(key)

    def get_node(self, key):
        """Returns the node name of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'nodename')

    def get_node_hostname(self, key):
        """Returns the hostname of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'hostname')

    def get_node_port(self, key):
        """Returns the port of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'port')

    def get_node_pos(self, key):
        """Returns the index position of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'pos')

    def get_node_weight(self, key):
        """Returns the weight of the node matching the hashed key.

        :param key: the key to look for.
        """
        return self._get(key, 'weight')

    def get_nodes(self):
        """Returns a list of the names of all the configured nodes.
        """
        return self._nodes.keys()

    def get_points(self):
        """Returns a ketama compatible list of (position, nodename) tuples.
        """
        return [(k, self._ring[k]) for k in self._keys]

    def get_server(self, key):
        """Returns a ketama compatible (position, nodename) tuple.

        :param key: the key to look for.
        """
        return self._get(key, 'tuple')

    def iterate_nodes(self, key, distinct=True):
        """hash_ring compatibility implementation.

        Given a string key it returns the nodes as a generator that
        can hold the key.
        The generator iterates one time through the ring
        starting at the correct position.
        if `distinct` is set, then the nodes returned will be unique,
        i.e. no virtual copies will be returned.
        """
        if not self._ring:
            yield None
        else:
            for node in self.range(key, unique=distinct):
                yield node['nodename']

    def print_continuum(self):
        """Prints a ketama compatible continuum report.
        """
        numpoints = len(self._keys)
        if numpoints:
            print('Numpoints in continuum: {}'.format(numpoints))
        else:
            print('Continuum empty')
        for p in self.get_points():
            point, node = p
            print('{} ({})'.format(node, point))

    def range(self, key, size=None, unique=True):
        """Returns a generator of nodes' configuration available
        in the continuum/ring.

        :param key: the key to look for.
        :param size: limit the list to at most this number of nodes.
        :param unique: a node may only appear once in the list (default True).
        """
        all_nodes = set()
        if unique:
            size = size or len(self._nodes)
        else:
            all_nodes = []

        pos = self._get_pos(key)
        for key in self._keys[pos:]:
            nodename = self._ring[key]
            if unique:
                if nodename in all_nodes:
                    continue
                all_nodes.add(nodename)
            else:
                all_nodes.append(nodename)
            yield self._nodes[nodename]
            if len(all_nodes) == size:
                break
        else:
            for i, key in enumerate(self._keys):
                if i < pos:
                    nodename = self._ring[key]
                    if unique:
                        if nodename in all_nodes:
                            continue
                        all_nodes.add(nodename)
                    else:
                        all_nodes.append(nodename)
                    yield self._nodes[nodename]
                    if len(all_nodes) == size:
                        break
