"""
bandcamp_tagplayer
Creates mpd playlists from Bandcamp genre tags.

Config file at: ~/.config/bandcamp_tagplayer/config

Usage:
  bandcamp_tagplayer
  bandcamp_tagplayer <tag>
  bandcamp_tagplayer (-h | --help)
  bandcamp_tagplayer (--version)

Options:
  -t --tag                  Search tag
  -h --help                 Show this screen.
  -v --version              Show version.
"""

""" Code:
Gregory Parrish
    http://github.com/greggparrish
"""

import os
from docopt import docopt
from slugify import slugify

from tagplayer import Tagplayer


if __name__ == '__main__':
    arguments = docopt(__doc__, version='bandcamp_tagplayer 1.0')
    if arguments['<tag>']:
        tag = slugify(arguments['<tag>'])
    else:
        tag = False
    try:
        with Tagplayer(tag) as tp:
            tp.check_tag()
    except Exception as e:
        print('ERROR: {}'.format(e))
