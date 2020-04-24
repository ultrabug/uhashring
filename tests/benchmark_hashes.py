# -*- coding: utf-8 -*-
"""This is not part of the test suite.
"""
from hashlib import md5, sha1, sha256
from time import time

num = 1000000
print("running {} key generation comparison".format(num))

# md5
pt = time()
for i in range(num):
    key = b"myval-%d" % i
    int(md5(b"%s" % key).hexdigest(), 16)
print("md5 took {} s".format(time() - pt))

# sha1
pt = time()
for i in range(num):
    key = b"myval-%d" % i
    int(sha1(b"%s" % key).hexdigest(), 16)
print("sha1 took {} s".format(time() - pt))

# sha256
pt = time()
for i in range(num):
    key = b"myval-%d" % i
    int(sha256(b"%s" % key).hexdigest(), 16)
print("sha256 took {} s".format(time() - pt))

# CityHash
try:
    from cityhash import CityHash32, CityHash64, CityHash128
except ImportError:
    print("CityHash not installed, pip install cityhash")
else:
    # cityhash32
    pt = time()
    for i in range(num):
        key = b"myval-%d" % i
        CityHash32(b"%s" % key)
    print("CityHash32 took {} s".format(time() - pt))

    # cityhash64
    pt = time()
    for i in range(num):
        key = b"myval-%d" % i
        CityHash64(b"%s" % key)
    print("CityHash64 took {} s".format(time() - pt))

    # cityhash128
    pt = time()
    for i in range(num):
        key = b"myval-%d" % i
        CityHash128(b"%s" % key)
    print("CityHash128 took {} s".format(time() - pt))

# murmurhash v3
try:
    import mmh3
except ImportError:
    print("MurmurHash v3 not installed, pip install murmurhash3")
else:
    pt = time()
    for i in range(num):
        key = b"myval-%d" % i
        mmh3.hash(b"%s" % key)
    print("MurmurHash v3 took {} s".format(time() - pt))
