#!/usr/bin/python3

"""
bandcamp_tagplayer
Creates mpd playlists from Bandcamp genre tags.

Config file at: ~/.config/bandcamp_tagplayer/config

Usage:
  bandcamp_tagplayer.py
  bandcamp_tagplayer.py <tag>
  bandcamp_tagplayer.py (-h | --help)
  bandcamp_tagplayer.py (--version)

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

from tagplayer import Tagplayer


def main():
  arguments = docopt(__doc__, version='bandcamp_tagplayer 1.0')
  bct = Tagplayer()
  if arguments['<tag>']:
    bct.monitor_mpd(arguments['<tag>'])
  else:
    bct.ask_for_tag()

if __name__ == '__main__':
    main()
