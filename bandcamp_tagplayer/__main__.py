"""
bandcamp_tagplayer
Config file at: ~/.config/bandcamp_tagplayer/config

Options:
  -h --help                 Show this screen.
  -v --version              Show version.
"""

""" Code:
Gregory Parrish
    https://github.com/greggparrish/bandcamp_tagplayer
"""

import os
import argparse

from tagplayer import Tagplayer


if __name__ == '__main__':
    p=argparse.ArgumentParser(description='Creates mpd playlists from Bandcamp genre tags.')
    p.add_argument('tag', help='Music genre', nargs='?', default=False)
    p.add_argument('-v', '--version', action='version', version='bandcamp_tagplayer v. 1.10')
    args=p.parse_args()

    tag = False
    if args.tag:
        tag = args.tag
    try:
        with Tagplayer(tag) as tp:
            tp.check_tag()
    except Exception as e:
        print(f'ERROR: {e}')
