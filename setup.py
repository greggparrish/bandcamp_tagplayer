import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3,0):
  sys.exit("Bandcamp_tagplayer requires python 3.")

VERSION = '1.0'

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
  required = f.read().splitlines()

setup(
    name='bandcamp_tagplayer',
    version=VERSION,
    description='Bandcamp_tagplayer creates an mpd playlist from Bandcamp songs by tag.',
    long_description=open('README.rst').read(),
    author='Gregory Parrish',
    author_email='gregg.alb@gmail.com',
    license='Unlicense',
    keywords=['bandcamp', 'tagplayer', 'music', 'cli', 'mpd', 'music tags'],
    url='http://github.com/greggparrish/bandcamp-tagplayer',
    packages=find_packages(),
    package_data={},
    install_requires=required,
    entry_points={
        'console_scripts': [
            'bandcamp-tagplayer=bandcamp_tagplayer.bandcamp_tagplayer:main',
        ],
    },
)
