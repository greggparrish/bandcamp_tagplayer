ABOUT
-----
Bandcamp_tagplayer pulls songs from Bandcamp based on tag and adds them to the current MPD playlist.

The file cache is cleaned on startup, removing files older than 24 hours.  


**Please support the artists.**


REQUIRES
--------
- Python 3
- MPD

INSTALL
-------
- Download zip
- unzip bandcamp_tagplayer-master.zip
- cd bandcamp_tagplayer-master
- pip3 install -r requirements.txt

CONFIG
------
- config file: ~/.config/bandcamp_tagplayer/config 
- set cache (dir for mp3s), and save_file (txt file to save artist info)
- set mpd host, port, and music directory 
- set browser (firefox, google-chrome, w3m) used to open artist page

USAGE
-----
- bandcamp_tagplayer.py <GENRE>
- ex. bandcamp_tagplayer.py darkwave
- hyphenate genres with more than one word, ex. new-wave, southern-gothic



