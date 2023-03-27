#!/usr/bin/env python
# coding: utf8
from setuptools import setup
import sys

VERSION = '5.1.2'

long_description = open('README.md').read()
install_requires_basic = [
    'coverage==7.2.2',
    'click==7.1.2',
    'click-datetime==0.2',
    'parameterized==0.8.1',
    'requests==2.27.1',
    'selenium==4.1.5',
    'urltools==0.4.0',
    'webdriver-manager==3.5.4',
]
install_requires_py_37 = [
    'numpy==1.21.6',
    'pandas==1.3.5',
]
install_requires_py_38_plus = [
    'numpy==1.24.2',
    'pandas==1.5.3',
]
if sys.version_info.minor == 7:
    install_requires_final = install_requires_basic + install_requires_py_37
else:
    install_requires_final = install_requires_basic + install_requires_py_38_plus


setup(name='finam-export',
      version=VERSION,
      description='Python library to download historical data from finam.ru',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='Apache-2',
      author='ffeast',
      author_email='ffeast@gmail.com',
      url='https://github.com/ffeast/finam-export',
      python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, <4',
      install_requires=install_requires_final,
      scripts=['scripts/finam-download.py', 'scripts/finam-lookup.py'],
      packages=['finam'])
