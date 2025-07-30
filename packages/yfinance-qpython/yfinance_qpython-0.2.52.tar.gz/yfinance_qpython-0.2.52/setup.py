#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# yfinance - market data downloader
# https://github.com/ranaroussi/yfinance

"""yfinance - market data downloader"""

from setuptools import setup, find_packages
# from codecs import open
import io
from os import path

# --- get version ---
version = "unknown"
with open("yfinance/version.py") as f:
    line = f.read().strip()
    version = line.replace("version = ", "").replace('"', '')
# --- /get version ---


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='yfinance-qpython',
    version=version,
    description='Download market data from Yahoo! Finance API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://qpypi.qpython.org/project/yfinance-qpython/',
    author='The QPYPI Team',
    author_email='qpypi@qpython.org',
    license='Apache',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Android",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
    ],
    platforms=['any'],
    keywords='pandas, yahoo finance, pandas datareader',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=['pandas-aipy', 'numpy-aipy',
                      'requests>=2.31', 'multitasking>=0.0.7',
                      'lxml-qpython', 'platformdirs>=2.0.0', 'pytz>=2022.5',
                      'frozendict>=2.3.4', 'peewee>=3.16.2',
                      'beautifulsoup4>=4.11.1', 'html5lib>=1.1'],
    extras_require={
        'nospam': ['requests_cache>=1.0', 'requests_ratelimiter>=0.3.1'],
        'repair': ['scipy-aipy'],
    },
    # Note: Pandas.read_html() needs html5lib & beautifulsoup4
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)

print("""
NOTE: yfinance is not affiliated, endorsed, or vetted by Yahoo, Inc.

You should refer to Yahoo!'s terms of use for details on your rights
to use the actual data downloaded.""")
