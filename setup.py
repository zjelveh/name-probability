import os
import sys
from setuptools import setup,Extension

from distutils.core import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_modules = cythonize([
    Extension(
        os.path.join('nameprobability', 'counter'),
        [os.path.join('nameprobability', 'counter.pyx')],
        extra_compile_args=['-O3', '-g0']
    )
])


setup(
    name='NameProbability',
    version='0.1.0',
    author='Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=['nameprobability'],
    #ext_modules = cythonize(["*.pyx"]),
    ext_modules=ext_modules,
    data_files=[('data', ['nameprobability/sample_names.csv', 'nameprobability/ss_data.pkl'])],
    description='Name matching tool',
    requires=[
        "Levenshtein",
        "NumPy",
        "cPickle",
        "name_cleaver"
    ],
)