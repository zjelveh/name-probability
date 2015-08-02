import os
import sys
from setuptools import setup,Extension

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from distutils.command.sdist import sdist as _sdist


class sdist(_sdist):
    def run(self):
        # Make sure the compiled Cython files in the distribution are up-to-date
        from Cython.Build import cythonize
        cythonize(['nameprobability/counter.pyx'])
        _sdist.run(self)

cmdclass = { }
cmdclass['sdist'] = sdist

numpy_core_dir = ''
#numpy_core_dir = '-I/export/home/zjelveh/.local/lib/python2.6/site-packages/numpy/core/include'

ext_modules = [
    Extension('counter', [ "nameprobability/counter.pyx" ],
        extra_compile_args=['-O3', '-g0', numpy_core_dir])
]
cmdclass.update({ 'build_ext': build_ext })


setup(
    name='NameProbability',
    version = '0.1.1',
    author = 'Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=['nameprobability'],
    cmdclass =  cmdclass,
    ext_modules = ext_modules,
    data_files = [('data', ['nameprobability/sample_names.csv', 'nameprobability/ss_data.pkl'])],
    description = 'Name matching tool',
    requires = [
        "Levenshtein",
        "NumPy",
        "cPickle"
    ],
)
