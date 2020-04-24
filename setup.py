"""
uhashring
"""

import os

from setuptools import find_packages, setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    author="Ultrabug",
    author_email="ultrabug@ultrabug.net",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description=(
        "Full featured consistent hashing python library compatible with ketama."
    ),
    download_url="https://github.com/ultrabug/uhashring/tags",
    include_package_data=True,
    install_requires=[],
    license="BSD",
    long_description=read("README.rst"),
    name="uhashring",
    packages=find_packages(),
    platforms="any",
    python_requires=">=2.7",
    url="https://github.com/ultrabug/uhashring",
    version="1.2",
    zip_safe=True,
)
