import os
import sys
from setuptools import setup,Extension

from distutils.core import setup

setup(
    name='NameProbability',
    version = '0.5.1',
    author = 'Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=['nameprobability'],
    data_files = [('data', ['nameprobability/sample_names.csv', 'nameprobability/ss_data.pkl'])],
    description = 'Name matching tool',
    requires = [
        "Levenshtein",
        "NumPy",
        "cPickle",
        "Numba"
    ],
)
