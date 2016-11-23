#!/usr/bin/python

import sys
import os
from setuptools import setup, find_packages

if sys.version_info < (3,0):
  sys.exit("Bandcamp_tagplayer requires python 3.")

version = '0.0.1'

setup(
    name='bandcamp_tagplayer',
    version=version,
    description='Bandcamp_tagplayer creates an mpd playlist from Bandcamp songs by tag.',
    long_description=open('README.rst').read(),
    author='Gregory Parrish',
    author_email='gregg.alb@gmail.com',
    license='Unlicense',
    keywords=['bandcamp', 'tagplayer', 'music', 'cli', 'mpd', 'music tags'],
    url='http://github.com/greggparrish/bandcamp-tagplayer',
    packages=find_packages(),
    package_data={},
    install_requires=[
        'beautifulsoup4>=4.5.1',
        'docopt>=0.6.2',
        'lxml>=3.6.4',
        'mutagen>=1.35.1',
        'python-mpd2'>='0.5.5',
        'slugify>=0.0.1',
    ],
    entry_points={
        'console_scripts': [
            'bandcamp-tagplayer=bandcamp_tagplayer.bandcamp_tagplayer:main',
        ],
    },
)
