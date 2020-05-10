#!/usr/bin/env python
# coding: utf8
from setuptools import setup

VERSION = '2.0.0'

long_description = open('README.md').read()

setup(name='finam-export',
      version=VERSION,
      description='Python library to download historical data from finam.ru',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='Apache-2',
      author='ffeast',
      author_email='ffeast@gmail.com',
      url='https://github.com/ffeast/finam-export',
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',
      install_requires=[
          'pandas>=0.24.2',
          'requests>=2.20.0, <3',
          'enum34',
          'click>=6.7',
          'click-datetime>=0.2'
      ],
      scripts=['scripts/finam-download.py', 'scripts/finam-lookup.py'],
      packages=['finam'])
