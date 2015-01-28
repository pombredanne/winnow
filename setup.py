#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

#here = path.abspath(path.dirname(__file__))
#with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
#    long_description = f.read()

setup(
    name='winnow',
    version='0.1',

    description='Separates files into NIST-known and NIST-unknown',
 #   long_description=long_description,
    url='https://github.com/rjhansen/winnow',
    author='Robert J. Hansen',
    author_email='rjh@sixdemonbag.org',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='NIST NSRL RDS',
    packages=find_packages(),
#    install_requires=['distutils>=0.3'],
    entry_points={
        'console_scripts': [
            'minnow=winnow:launcher',
        ],
    },
)