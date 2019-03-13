import argparse
from tagplayer import Tagplayer

"""
bandcamp_tagplayer
Config file at: ~/.config/bandcamp_tagplayer/config

Options:
  -h --help                 Show this screen.
  -v --version              Show version.

Code:
    Gregory Parrish
    https://github.com/greggparrish/bandcamp_tagplayer
"""

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Creates mpd playlists from Bandcamp genre tags.')
    p.add_argument('tag', help='Music genre', nargs='?', default=False)
    p.add_argument('-t', '--tag', help='Music genre', action='store', default=False)
    p.add_argument('-u', '--user', help='Bandcamp username', action='store', default=False)
    p.add_argument('-v', '--version', action='version', version='bandcamp_tagplayer v. 1.20')
    args = p.parse_args()

    tag = None
    user= None

    try:
        with Tagplayer(tag=args.tag, user=args.user) as tp:
            tp.check_tag()
    except Exception as e:
        print(f'ERROR: {e}')
