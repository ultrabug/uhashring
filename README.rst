*********
uhashring
*********
|version|

.. |version| image:: https://img.shields.io/pypi/v/uhashring.svg

**uhashring** implements **consistent hashing** in pure python and is fully compatible with `ketama <https://github.com/RJ/ketama>`_.

Consistent hashing is mostly used on distributed systems/caches/databases as this avoid the total reshuffling of your key-node mappings when adding or removing a node in your ring (called continuum on libketama). More information and details about this can be found in the *literature* section.

This full featured implementation offers:

- a lot of **convenient methods** to use your consistent hash ring in real world applications.
- simple **integration** with other libs such as memcache through monkey patching.
- all the missing functions in the libketama C python binding (which is not even available on pypi).
- another and more performant consistent hash algorithm if you don't care about the ketama compatibility (see benchmark).
- **instance-oriented usage** so you can use your consistent hash ring object directly in your code (see advanced usage).
- native **pypy support**.
- tests of implementation, key distribution and ketama compatibility.

**uhashring** default is to be compatible with the ketama implementation so you get 40 vnodes and 4 replicas = 160 points per node in the ring. Per node weight is also supported and will affect the nodes distribution on the ring.

Usage
=====
Basic usage
-----------
**uhashring** is very simple and efficient to use:
::

    from uhashring import HashRing

    # create a consistent hash ring of 3 nodes of weight 1
    hr = HashRing(nodes=['node1', 'node2', 'node3'])

    # get the node name for the 'coconut' key
    target_node = hr.get_node('coconut')

Advanced usage
--------------
::

    from uhashring import HashRing

    # Mapping of dict configs
    # Ommited config keys will get a default value, so
    # you only need to worry about the ones you need
    nodes = {
        'node1': {
                'hostname': 'node1.fqdn',
                'instance': memcache.Client(['node1.fqdn:11211']),
                'port': 11211,
                'vnodes': 40,
                'weight': 1
            },
        'node2': {
                'hostname': 'node2.fqdn',
                'instance': memcache.Client(['node2.fqdn:11211']),
                'port': 11211,
                'vnodes': 40
            },
        'node3': {
                'hostname': 'node3.fqdn',
                'instance': memcache.Client(['node3.fqdn:11211']),
                'port': 11211
            }
        }

    # create a new consistent hash ring with the nodes
    hr = HashRing(nodes)

    # set the 'coconut' key/value on the right host's memcache instance
    hr['coconut'].set('coconut', 'my_value')

    # get the 'coconut' key from the right host's memcache instance
    hr['coconut'].get('coconut')

    # delete the 'coconut' key on the right host's memcache instance
    hr['coconut'].delete('coconut')

    # get the node config for the 'coconut' key
    conf = hr.get('coconut')

Default node configuration
--------------------------
**uhashring** offers advanced node configuration for real applications, this is the default you get for every added node:
::

    {
        'hostname': <nodename>,
        'instance': None,
        'port': None,
        'vnodes': 40,
        'weight': 1
    }

Adding / removing nodes
-----------------------
You can add and remove nodes from your consistent hash ring at any time.
::

    from uhashring import HashRing

    # this is a 3 nodes consistent hash ring
    hr = HashRing(nodes=['node1', 'node2', 'node3'])

    # this becomes a 2 nodes consistent hash ring
    hr.remove_node('node2')

    # add back node2
    hr.add_node('node2')

    # add node4 with a weight of 10
    hr.add_node('node4', {'weight': 10})

HashRing options
----------------
- **nodes**: nodes used to create the continuum (see doc for format).
- **replicas**: number of replicas per node (forced to 4 in compatibility mode).
- **vnodes**: default number of vnodes per node.
- **compat**: use a ketama compatible hash calculation (default True).

Available methods
-----------------
- **add_node(nodename, conf)**: add (or overwrite) the node in the ring with the given config.
- **get(key)**: returns the node object dict matching the hashed key.
- **get_key(key)**: alias of ketama hashi method, returns the hash of the given key.
- **get_node(key)**: returns the node name of the node matching the hashed key.
- **get_node_hostname(key)**: returns the hostname of the node matching the hashed key.
- **get_node_instance(key)**: returns the instance of the node matching the hashed key.
- **get_node_port(key)**: returns the port of the node matching the hashed key.
- **get_node_pos(key)**: returns the index position of the node matching the hashed key.
- **get_node_weight(key)**: returns the weight of the node matching the hashed key.
- **get_nodes()**: returns a list of the names of all the configured nodes.
- **get_points()**: returns a ketama compatible list of (position, nodename) tuples.
- **get_server(key)**: returns a ketama compatible (position, nodename) tuple.
- **hashi(key)**: returns the hash of the given key (on compat mode, this is the same as libketama).
- **iterate_nodes(key, distinct)**: hash_ring compatibility implementation, same as range but returns tuples as a generator.
- **print_continuum()**: prints a ketama compatible continuum report.
- **range(key, size, unique)**: returns a (unique) list of max (size) nodes' configuration available in the consistent hash ring.
- **remove_node(nodename)**: remove the given node from the ring

Available properties
--------------------
- **conf**: dict of all the nodes and their configuration.
- **continuum**: same as ring.
- **distribution**: counter of the nodes distribution in the consistent hash ring.
- **ring**: hash key/node mapping of the consistent hash ring.
- **size**: size of the consistent hash ring.

Integration (monkey patching)
=============================
You can benefit from a consistent hash ring using **uhashring** monkey patching on the following libraries:

python-memcached
----------------
::

    import memcache

    from uhashring import monkey
    monkey.patch_memcache()

    mc = memcache.Client(['node1:11211', 'node2:11211'])

Installation
============
Pypi
----
Using pip:
::

    $ pip install uhashring

Gentoo Linux
------------
Using emerge:
::

    $ sudo emerge -a uhashring

Benchmark
=========
Usage of the ketama compatible hash (default) has some performance impacts.
Contributions are welcome as to ways of improving this !
::

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

    hr = HashRing(nodes=[], compat=False)

    Quick benchmark, for 1 million generated hash keys:
        - python 2: 3.7595579624176025 ms
        - python 3: 3.268343687057495 ms
        - pypy: 1.9193649291992188 ms

Literature
==========
- consistent hashing: https://en.wikipedia.org/wiki/Consistent_hashing
- web caching paper: http://www8.org/w8-papers/2a-webserver/caching/paper2.html
- research paper: http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.23.3738
- distributed hash table: https://en.wikipedia.org/wiki/Distributed_hash_table
