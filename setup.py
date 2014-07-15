#! /usr/bin/env python
# ===============================================
# python setup.py register sdist bdist_egg upload
# USE TWINE INSTEAD
# ===============================================
from setuptools import setup


def fread(filename, split=False, keepnl=False):
    """
    may raise IOError exceptions from file operations
    """
    result = ""
    if split:
        result = []
    with open(filename) as f:
        for line in f:
            tmpline = line
            if line == '\n':
                continue
            if split:
                if '#' in tmpline.strip()[:2]:
                    continue
                result.append(line.replace('\n', ''))
            else:
                result += line
    return result


PROJECT = "machop"
AUTHOR = "Bryce Eggleton"
EMAIL = "None"
DESC = "Automation, CI, and filewatching tools for Python projects"
LONG_DESC = fread('README.rst')
LICENSE = "BSD License"
KEYWORDS = "automation flake8 py.test watch"
URL = "http://packages.python.org/machop"
REQUIRES = fread('requirements.txt', True)

# @@@ write function to read version from version.py or __init__.py file
VERSION = "0.1.0"

TAGS = [
    "Development Status :: 2 - Pre-Alpha",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: BSD License",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 2.7",
    ]
# https://pypi.python.org/pypi?%3Aaction=list_classifiers


setup(
    name=PROJECT,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESC,
    license=LICENSE,
    keywords=KEYWORDS,
    url=URL,
    packages=['machop'],
    long_description=LONG_DESC,
    install_requires=REQUIRES,
    classifiers=TAGS,
    entry_points={
        "console_scripts": ['machop = machop.__main__:run_machop_cli'],
    },
)
