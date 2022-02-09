from setuptools import setup, find_packages
from os import path
import sys

from io import open
here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join(here, 'meteor_reasoner'))
from version import __version__

print('version')
print(__version__)

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='meteor_reasoner',
      version=__version__,
      description='A Metric Temporal Reasoner',
      url='https://github.com/wdimmy/MeTeoR',
      author='Dingmin Wang',
      author_email='dingmin.wang@cs.ox.ac.uk',
      keywords=['DatalogMTL', 'Knowledge Representation', 'Temporal Reasoning'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires = [
        'outdated>=0.2.0'
      ],
      license='MIT',
      packages=find_packages(exclude=["data"]),
      extras_require={
          "interactive" : ['matplotlib>=2.2.0', 'jupyter']
      },
      setup_requires=['pytest-runner'],
      tests_require=["pytest"],
      include_package_data=True,
      classifiers=[
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
