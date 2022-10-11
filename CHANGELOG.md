# CHANGELOG

## version 2.2
* support for python 3.10
* drop support of EOL python 3.6
* migrate to hatch
* add CHANGELOG
* fix test_distribution to be deterministic (using randint causes a fai… (#17), by Ben Hockley
* ci: add github actions

## version 2.1
* document ketama ring replicas configuration
* makefile: add clean, release and test targets
* add paypal funding
* tox: add gh-actions mapping

## version 2.0
* python3.6+ syntax update and code QA
* add project funding information
* tox: update tox tests to the correct python versions
* Expose replicas argument for KetamaRing, by Sebastian Lohff
* Merge pull request #14 from sebageek/expose-ketama-replicas

## version 1.1
* Copyright bump., by Gabriel Linder
* Drop old pythons, add new ones., by Gabriel Linder
* Allow to pass options to pytest., by Gabriel Linder
* Merge pull request #9 from dargor/cleanup
* code qa: apply black, isort, flake8
* Merge pull request #11 from ultrabug/qa
* tests: update tox and setup settings
* tox: add pypy3 tests
* qa: ignore tox folder
* readme: mention python2 end of life
* Wrong TCP port for Redis in the "advanced usage" section., by Babacar TALL
* Merge pull request #12 from btall/readme/fix-typo-advanced-usage

## version 1.0
* Use hash_fn parameter, by Chris Woo
* Add bracket, by Chris Woo
* Merge pull request #8 from krisdestruction/patch-1
* ignore pytest cache
* respect pep8
* add tests for hash_fn usage thx to #8

## version 0.8
* split ring implementations into modules, faster md5 ring rewrite
* switch to md5 implementation as default, change the hashring signature
* Merge pull request #7 from ultrabug/mod_rings_and_new_sig
* add ketama collision test thx to @bjhockley wrt issue #6

## version 0.7
* fix python3 python-memcached monkey patching and tests thx to @garrylachman, fixes #5

## version 0.6
* update the README for user defined hash function
* dont force vnodes and replicas when using an external hash function

## version 0.5
* rename _hashi_faster to _hashi_md5
* add new hash_fn option to allow passing a custom hash function for the ring

## version 0.4
* Avoid the exception AttributeError: can't set attribute, in the case of executed test suite with an version of setuptools greater than 18.3, by Babacar Tall
* unit test: Add the compatibility for python 3, by Babacar Tall
* Adding of envtest=py35 in the tox.ini, by Babacar Tall
* Added tox.ini file in the MANIFEST.in, by Babacar Tall
* Merge pull request #2 from btall/fix/python3-setup-test
* fix ridiculous time error
* add hashes simple benchmarking code
* add tests on ring growth
* performance: avoid ring recalculation

## version 0.3
* allow benchmark to run without ketama
* map has better performance than comprehension list thx to @btall
* implement a weight_fn parameter allowing users to pass their own weight calculation function to the hash ring
* add tests for weight_fn implementation
* document and demonstrate the weight_fn implementation

## version 0.2
* add get_instances method to get a list of all available instances on the ring
* ring.nodes is an alias of ring.conf for convenience
