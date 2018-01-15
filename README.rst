ABOUT
-----
Bandcamp_tagplayer pulls songs from Bandcamp based on tag and adds them to the current MPD playlist.

The file cache is cleaned on startup, removing files older than 24 hours.

**Please support the artists.**


REQUIRES
--------
- **Python 3.6**
- MPD

INSTALL
-------
- Download zip
- unzip bandcamp_tagplayer-master.zip
- cd bandcamp_tagplayer-master
- pip3 install -r requirements.txt (or pipenv install)

CONFIG
------
- config file: ~/.config/bandcamp_tagplayer/config
- set cache (dir for mp3s), and save_file (txt file to save artist info)
- set mpd host, port, and music directory
- check out config.example for all options

USAGE
-----
- bandcamp_tagplayer <TAG>
- ex. bandcamp_tagplayer darkwave
- if genre contains spaces, hyphenate it or use quotation marks.
- ex. bandcamp_tagplayer new-wave
- ex. bandcamp_tagplayer 'new wave'
