# -*- coding: utf8 -*-

from setuptools import setup

from os import path
import io
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    longdesc = f.read()

setup(
    name='html2markdown',
    py_modules=['html2markdown'],
    version='0.1.6.post0',
    description='Conservatively convert html to markdown',
    author='David Lönnhager',
    author_email='dv.lnh.d@gmail.com',
    url='https://github.com/dlon/html2markdown',
    install_requires=[
        'beautifulsoup4'
    ],
    long_description=longdesc,
    long_description_content_type='text/x-rst',
)
