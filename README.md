# uhashring

![version](https://img.shields.io/pypi/v/uhashring.svg)
![ci](https://github.com/ultrabug/uhashring/actions/workflows/ci.yml/badge.svg)

**uhashring** implements **consistent hashing** in pure Python.

Consistent hashing is mostly used on distributed
systems/caches/databases as this avoid the total reshuffling of your
key-node mappings when adding or removing a node in your ring (called
continuum on libketama). More information and details about this can be
found in the *literature* section.

This full featured implementation offers:

-   a lot of **convenient methods** to use your consistent hash ring in
    real world applications.
-   simple **integration** with other libs such as memcache through
    monkey patching.
-   a full [ketama](https://github.com/RJ/ketama) compatibility if you
    need to use it (see important mention below).
-   all the missing functions in the libketama C python binding (which
    is not even available on pypi) for ketama users.
-   possibility to **use your own weight and hash functions** if you
    don't care about the ketama compatibility.
-   **instance-oriented usage** so you can use your consistent hash ring
    object directly in your code (see advanced usage).
-   native **pypy support**, since this is a pure python library.
-   tests of implementation, key distribution and ketama compatibility.

Per node weight is also supported and will affect the nodes distribution
on the ring.

## Python 2 EOL

If you need Python 2 support, make sure to use **uhashring==1.2** as
v1.2 is the last release that will support it.

## IMPORTANT

Since v1.0 **uhashring** default has changed to use a md5 hash function
with 160 vnodes (points) per node in the ring.

This change was motivated by the fact that the ketama hash function has
more chances of collisions and thus requires a complete ring
regeneration when the nodes topology change. This could lead to degraded
performances on rapidly changing or unstable environments where nodes
keep going down and up. The md5 implementation provides a linear
performance when adding or removing a node from the ring!

Reminder: when using **uhashring** with the ketama implementation and
get 40 vnodes and 4 replicas = 160 points per node in the ring.

## Usage

### Basic usage

**uhashring** is very simple and efficient to use:

```python
from uhashring import HashRing

# create a consistent hash ring of 3 nodes of weight 1
hr = HashRing(nodes=['node1', 'node2', 'node3'])

# get the node name for the 'coconut' key
target_node = hr.get_node('coconut')
```

### Ketama usage

Simply set the **hash_fn** parameter to **ketama**:

```python
from uhashring import HashRing

# create a consistent hash ring of 3 nodes of weight 1
hr = HashRing(nodes=['node1', 'node2', 'node3'], hash_fn='ketama')

# get the node name for the 'coconut' key
target_node = hr.get_node('coconut')
```

### Advanced usage

```python
from uhashring import HashRing

# Mapping of dict configs
# Omitted config keys will get a default value, so
# you only need to worry about the ones you need
nodes = {
    'node1': {
            'hostname': 'node1.fqdn',
            'instance': redis.StrictRedis(host='node1.fqdn'),
            'port': 6379,
            'vnodes': 40,
            'weight': 1
        },
    'node2': {
            'hostname': 'node2.fqdn',
            'instance': redis.StrictRedis(host='node2.fqdn'),
            'port': 6379,
            'vnodes': 40
        },
    'node3': {
            'hostname': 'node3.fqdn',
            'instance': redis.StrictRedis(host='node3.fqdn'),
            'port': 6379
        }
    }

# create a new consistent hash ring with the nodes
hr = HashRing(nodes)

# set the 'coconut' key/value on the right host's redis instance
hr['coconut'].set('coconut', 'my_value')

# get the 'coconut' key from the right host's redis instance
hr['coconut'].get('coconut')

# delete the 'coconut' key on the right host's redis instance
hr['coconut'].delete('coconut')

# get the node config for the 'coconut' key
conf = hr.get('coconut')
```

### Default node configuration

**uhashring** offers advanced node configuration for real applications,
this is the default you get for every added node:

```python
{
    'hostname': nodename,
    'instance': None,
    'port': None,
    'vnodes': 40,
    'weight': 1
}
```

### Adding / removing nodes

You can add and remove nodes from your consistent hash ring at any time.

```python
from uhashring import HashRing

# this is a 3 nodes consistent hash ring
hr = HashRing(nodes=['node1', 'node2', 'node3'])

# this becomes a 2 nodes consistent hash ring
hr.remove_node('node2')

# add back node2
hr.add_node('node2')

# add node4 with a weight of 10
hr.add_node('node4', {'weight': 10})
```

### Customizable node weight calculation

```python
from uhashring import HashRing

def weight_fn(**conf):
    """Returns the last digit of the node name as its weight.

    :param conf: node configuration in the ring, example:
        {
         'hostname': 'node3',
         'instance': None,
         'nodename': 'node3',
         'port': None,
         'vnodes': 40,
         'weight': 1
        }
    """
    return int(conf['nodename'][-1])

# this is a 3 nodes consistent hash ring with user defined weight function
hr = HashRing(nodes=['node1', 'node2', 'node3'], weight_fn=weight_fn)

# distribution with custom weight assignment
print(hr.distribution)

# >>> Counter({'node3': 240, 'node2': 160, 'node1': 80})
```

### Customizable hash function

```python
from uhashring import HashRing

# import your own hash function (must be a callable)
# in this example, MurmurHash v3
from mmh3 import hash as m3h

# this is a 3 nodes consistent hash ring with user defined hash function
hr = HashRing(nodes=['node1', 'node2', 'node3'], hash_fn=m3h)

# now all lookup operations will use the m3h hash function
print(hr.get_node('my key hashed by your function'))
```

### HashRing options

-   **nodes**: nodes used to create the continuum (see doc for format).
-   **hash_fn**: use this callable function to hash keys, can be set to
    'ketama' to use the ketama compatible implementation.
-   **vnodes**: default number of vnodes per node.
-   **weight_fn**: user provided function to calculate the node's
    weight, gets the node conf dict as kwargs.
-   **replicas**: use this to change ketama ring replicas (default: 4)

### Available methods

-   **add_node(nodename, conf)**: add (or overwrite) the node in the
    ring with the given config.
-   **get(key)**: returns the node object dict matching the hashed key.
-   **get_key(key)**: alias of the current hashi method, returns the
    hash of the given key.
-   **get_instances()**: returns a list of the instances of all the
    configured nodes.
-   **get_node(key)**: returns the node name of the node matching the
    hashed key.
-   **get_node_hostname(key)**: returns the hostname of the node
    matching the hashed key.
-   **get_node_instance(key)**: returns the instance of the node
    matching the hashed key.
-   **get_node_port(key)**: returns the port of the node matching the
    hashed key.
-   **get_node_pos(key)**: returns the index position of the node
    matching the hashed key.
-   **get_node_weight(key)**: returns the weight of the node matching
    the hashed key.
-   **get_nodes()**: returns a list of the names of all the configured
    nodes.
-   **get_points()**: returns a ketama compatible list of (position,
    nodename) tuples.
-   **get_server(key)**: returns a ketama compatible (position,
    nodename) tuple.
-   **hashi(key)**: returns the hash of the given key (on ketama mode,
    this is the same as libketama).
-   **iterate_nodes(key, distinct)**: hash_ring compatibility
    implementation, same as range but returns tuples as a generator.
-   **print_continuum()**: prints a ketama compatible continuum report.
-   **range(key, size, unique)**: returns a (unique) list of max (size)
    nodes' configuration available in the consistent hash ring.
-   **regenerate**: regenerate the ring from the current nodes
    configuration, useful only when using *weight_fn*.
-   **remove_node(nodename)**: remove the given node from the ring

### Available properties

-   **conf**: dict of all the nodes and their configuration.
-   **continuum**: same as ring.
-   **distribution**: counter of the nodes distribution in the
    consistent hash ring.
-   **nodes**: same as conf.
-   **ring**: hash key/node mapping of the consistent hash ring.
-   **size**: size of the consistent hash ring.

## Integration (monkey patching)

You can benefit from a consistent hash ring using **uhashring** monkey
patching on the following libraries:

### python-memcached

```python
import memcache

from uhashring import monkey
monkey.patch_memcache()

mc = memcache.Client(['node1:11211', 'node2:11211'])
```

## Installation

### Pypi

Using pip:

```bash
$ pip install uhashring
```

### Gentoo Linux

Using emerge:

```bash
$ sudo emerge -a uhashring
```

## Benchmark

Usage of the ketama compatible hash (default) has some performance
impacts. Contributions are welcome as to ways of improving this !

> There is a big performance gap in the hash calculation between the
> ketama C binding and its pure python counterpart.
>
> Python 3 is doing way better than python 2 thanks to its native
> bytes/int representation.
>
> ***Quick benchmark, for 1 million generated ketama compatible keys:***
> -   python_ketama C binding: 0.8427069187164307 s
> -   python 2: 5.462762832641602 s
> -   python 3: 3.570068597793579 s
> -   pypy: 1.6146340370178223 s
>
> When using python 2 and ketama compatibility is not important, you can
> get a better hashing speed using the other provided hashing.
>
> hr = HashRing(nodes=[], compat=False)
>
> ***Quick benchmark, for 1 million generated hash keys:***
> -   python 2: 3.7595579624176025 s
> -   python 3: 3.268343687057495 s
> -   pypy: 1.9193649291992188 s

## Literature

-   consistent hashing:
    <https://en.wikipedia.org/wiki/Consistent_hashing>
-   web caching paper:
    <http://www8.org/w8-papers/2a-webserver/caching/paper2.html>
-   research paper:
    <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.23.3738>
-   distributed hash table:
    <https://en.wikipedia.org/wiki/Distributed_hash_table>

## License

BSD
