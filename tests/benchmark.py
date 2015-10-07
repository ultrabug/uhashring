# -*- coding: utf-8 -*-
"""This is not part of the test suite.
"""
import ketama

from time import time
from tempfile import NamedTemporaryFile
from uhashring import HashRing

num = 1000000
print('running {} key generation comparison'.format(num))

# ketama C binding
with NamedTemporaryFile(prefix='benchmark_') as ketama_config_file:
    ketama_config_file.write("127.0.0.1:11211\t600\n")
    ketama_config_file.write("127.0.0.1:11212\t400\n")
    ketama_config_file.flush()

    kt = ketama.Continuum(ketama_config_file.name)
    pt = time()
    for i in range(num):
        key = 'myval-{}'.format(i)
        kt.get_server(key)
    print('ketama took {} ms'.format(time() - pt))

# pure python implementation
ring = HashRing(
    nodes={'127.0.0.1:11211': 600,
           '127.0.0.1:11212': 400},
    replicas=4,
    vnodes=40,
    compat=True)
pt = time()
for i in range(num):
    key = 'myval-{}'.format(i)
    ring.get_server(key)
print('HashRing took {} ms'.format(time() - pt))
