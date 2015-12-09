#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Ivan Lalashkov.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
#from distutils.core import setup
from setuptools import setup
import codecs
import os

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = 'rutracker.py'
VERSION = '1.0.0'
DESCRIPTION = 'Command-line tool that downloads torrent files from Rutracker.org.'
AUTHOR = 'Ivan Lalashkov'
AUTHOR_EMAIL = 'lalashkov.ivan@gmail.com'
URL = 'https://github.com/van-gog/rutracker.py'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='MIT',
    url=URL,
    py_modules=['rutracker'],
    entry_points={
        'console_scripts': [
            'rutracker=rutracker:main'
        ]
    }
)

