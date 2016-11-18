#!/usr/bin/python

from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='bandcamp-tagplayer',
    version=version,
    description='bandcamp-tagplayer creates a radio stream from Bandcamp tags.',
    long_description=open('README.md').read(),
    author='Gregory Parrish',
    author_email='gregg.alb@gmail.com',
    license='Unlicense',
    keywords=['bandcamp', 'tagplayer', 'music', 'cli', 'albums', 'dl'],
    url='http://github.com/greggparrish/bandcamp-tagplayer',
    packages=find_packages(),
    package_data={},
    install_requires=[
        'beautifulsoup4>=4.5.1',
        'docopt>=0.6.2',
        'lxml>=3.6.4',
        'mutagen>=1.35.1',
        'ply>=3.9',
        'slimit>=0.8.1',
        'slugify>=0.0.1',
        'wgetter>=0.6',
    ],
    entry_points={
        'console_scripts': [
            'bandcamp-tagplayer=bandcamp_tagplayer.bandcamp_tagplayer:main',
        ],
    },
)
