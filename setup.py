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

ext_modules = [
    #Extension(os.path.join('nameprobability', 'counter'), [ "nameprobability/counter.pyx" ])
    Extension('nameprobability', [ "nameprobability/counter.pyx" ],
        extra_compile_args=['-O3', '-g0', 
        '-I/export/home/zjelveh/vvv/lib/python2.6/site-packages/numpy/core/include/'])
]
cmdclass.update({ 'build_ext': build_ext })

# ext_modules = cythonize([
#    Extension(
#        os.path.join('nameprobability', 'counter'),
#        [os.path.join('nameprobability', 'counter.pyx')],
#        extra_compile_args=['-O3', '-g0']
#    )
# ])
# ext_modules = cythonize(os.path.join('nameprobability', 'counter'))

setup(
    name='NameProbability',
    version = '0.1.0',
    author = 'Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=['nameprobability'],
    #ext_modules = cythonize(["*.pyx"]),
    cmdclass =  cmdclass,
    ext_modules = ext_modules,
    data_files = [('data', ['nameprobability/sample_names.csv', 'nameprobability/ss_data.pkl'])],
    description = 'Name matching tool',
    requires = [
        "Levenshtein",
        "NumPy",
        "cPickle",
        "name_cleaver"
    ],
)
