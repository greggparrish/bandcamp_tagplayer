ABOUT
-----
bandcamp_tagplayer pulls songs from Bandcamp based on genre tag or username and adds them to the current MPD playlist.

The file cache is cleaned on startup, removing files older than 24 hours.

**Please support the artists.**


REQUIRES
--------
- **Python 3.6**
- MPD

INSTALL
-------
- wget https://github.com/greggparrish/bandcamp_tagplayer/archive/master.tar.gz -O bandcamp_tagplayer.tar.gz
- pip install bandcamp_tagplayer.tar.gz

CONFIG
------
- config file: ~/.config/bandcamp_tagplayer/config
- set cache (dir for mp3s), mpd host, port, and music directory
- check out config.example for all options

USAGE
-----
- bandcamp_tagplayer <TAG>
- ex: bandcamp_tagplayer darkwave
- If the genre contains spaces, hyphenate it or use quotation marks.
- ex: bandcamp_tagplayer new-wave
- ex: bandcamp_tagplayer 'new wave'
- Use --user to stream a user's collection.
- bandcamp_tagplayer --user <USERNAME>
- ex: bandcamp_tagplayer --user realredadax
