import os
import sys
from setuptools import setup, Extension

from distutils.core import setup

setup(
    name='NameProbability',
    version = '0.5.1',
    author = 'Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=[''],
    data_files = [('data', ['sample_names.csv'])],
    description = 'Name matching tool',
    requires = [
        "Levenshtein",
        "NumPy",
        "Numba"
    ],
)
