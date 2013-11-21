from distutils.core import setup

setup(
    name='NameProbability',
    version='0.1.0',
    author='Zubin Jelveh',
    author_email='zj292@nyu.edu',
    packages=['nameprobability', ''],
    description='Name matching tool',
    install_requires=[
        "Levenshtein",
        "NumPy",
    ],
)