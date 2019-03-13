import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Bandcamp_tagplayer requires python <= 3.6.")

VERSION = '1.30'

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(
    name='bandcamp_tagplayer',
    version=VERSION,
    description='Bandcamp_tagplayer creates an mpd playlist from Bandcamp songs by tag or user.',
    long_description=open('README.rst').read(),
    author='Gregory Parrish',
    author_email='grp224@nyu.edu',
    license='Unlicense',
    keywords=['bandcamp', 'tagplayer', 'music', 'cli', 'mpd', 'music tags', 'music genres'],
    url='https://github.com/greggparrish/bandcamp_tagplayer',
    packages=find_packages(),
    package_data={},
    install_requires=required,
    entry_points={
        'console_scripts': [
            'bandcamp-tagplayer=bandcamp_tagplayer.bandcamp_tagplayer:main',
        ],
    },
)
