#!/usr/bin/python3

"""
  - get album_metadata
  - ban_songs
  - ban_album
"""

import datetime
import os
import webbrowser

from mutagen.easyid3 import EasyID3
import config

web_app = config.browser
save_file = config.save_file
cache_dir = config.cache_dir
music_dir = config.music_dir

def browser(filename):
  artist_url = EasyID3(os.path.join(music_dir,filename))['website'][0]
  webbrowser.get(web_app).open(artist_url)

def save_track_info(filename):
  date = datetime.datetime.now()
  track = EasyID3(os.path.join(music_dir,filename))
  info = ['\n']
  info += track['website'][0]
  info += track['artist'][0]
  info += track['title'][0]
  info += track['album'][0]
  ('\n').join(info)
  with open(save_file, 'a') as out:
    out.write(artist + '\n')
