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
  date = str(datetime.datetime.now())
  track = EasyID3(os.path.join(music_dir,filename))
  artist = track['artist'][0]
  song = track['title'][0]
  album = track['album'][0]
  website = track['website'][0]
  with open(save_file, 'a') as out:
    out.write('\n'+date+'\n'+artist+'\n'+song+'\n'+website + '\n')
  pass

def ban(item_id,item_type):
  pass

def clear_cache():
  files = filter(os.path.isfile, os.listdir( cache_dir ) )
  files = [ f for f in os.listdir( 'home/ezra/' ) if os.path.isfile(f) ]
  for f in files:
    print(f)



