"""
uhashring
"""

import os
import sys

from pkg_resources import get_distribution, parse_version
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)

        # https://bitbucket.org/pypa/setuptools/commits/cf565b6
        if get_distribution('setuptools').parsed_version < parse_version('18.4'):
            self.test_args = []
            self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    author='Ultrabug',
    author_email='ultrabug@ultrabug.net',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={'test': PyTest},
    description='Consistent hashing implementation compatible with the ketama hash ring.',
    download_url='https://github.com/ultrabug/uhashring/tags',
    include_package_data=True,
    install_requires=[],
    license='BSD',
    long_description=read('README.rst'),
    name='uhashring',
    packages=find_packages(),
    platforms='any',
    tests_require=['python-memcached', 'pytest'],
    url='https://github.com/ultrabug/uhashring',
    version='0.6',
    zip_safe=True)
