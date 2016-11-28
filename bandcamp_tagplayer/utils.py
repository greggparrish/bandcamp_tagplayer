#!/usr/bin/python3

import datetime
import os
import re
import time
import webbrowser

from blessed import Terminal
from mutagen.easyid3 import EasyID3

import config
import db
from messages import Messages

web_app = config.browser
save_file = config.save_file
cache_dir = config.cache_dir
music_dir = config.music_dir

class Utils:
  def build_dirs(self):
    """ Create bandcamp_tagplayer dir and cache dir in .config """
    path = cache_dir
    if not os.path.exists(path):
      os.makedirs(path)
    return path

  def copy_conf(self):
    """ Copy over conf file if it doesn't exist """ 
    pass 

  def symlink_musicdir(self):
    """ Cache has to be within mpd music dir to load tracks,
        so symlink it if user didn't choose a path already in
        their mpd music dir """
    try:
      os.symlink(cache_dir,music_dir)
    except FileExistsError:
      pass

  def browser(self,filename):
    """ Open browser with Bandcamp artist url """
    artist_url = EasyID3(os.path.join(music_dir,filename))['website'][0]
    wb = webbrowser.get(web_app).open(artist_url)
    return wb

  def save_track_info(self,current_song):
    """ Save artist, trac, genre & url to text file set in config """
    term = Terminal()
    print(term.normal) 
    date = '{0:%b %d, %Y %H:%M:%S}'.format(datetime.datetime.now())
    track = EasyID3(os.path.join(music_dir,current_song))
    artist = "Artist: {}".format(track['artist'][0])
    song = "Track: {}".format(track['title'][0])
    genre = "Genre: {}".format(track['genre'][0])
    website = track['website'][0]
    with open(save_file, 'a') as out:
      saved = out.write('\n'+date+'\n'+artist+'\n'+song+'\n'+genre+'\n'+website + '\n')
    return saved

  def ban(self,item_id,item_type):
    """ Ban either a track or artisti, won't dl in future """
    banned = db.Database.ban_item(item_id,item_type)
    return banned

  def clear_cache(self):
    """ Remove Bandcamp mp3s from cache dir if older than a day """
    now_ts = int(time.time())
    files = [f for f in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir,f))]
    for f in files:
      bc_track = re.findall('bctcache_\d*_\d*_\d*.mp3', f)
      if bc_track:
        ts =  int(bc_track[0].split('_')[1])
        if ts+86400 < now_ts:
          os.remove(os.path.join(cache_dir,bc_track[0]))

  def options_menu(self,current_song):
    """ Render options menu and handle commands """
    term = Terminal()
    change = False
    with term.location(0, term.height - 1):
      with term.cbreak():
        c = term.inkey(1)
        if c == 'c':
          print(term.clear())
          change = True
          print(change)
          return change
          pass
        if c =='q':
          print(term.clear())
          print(term.normal)
          self.clear_cache()
          exit()
        if c == 'B':
          ar_id = current_song.split('_')[2]
          self.ban(ar_id,0)
          show = 'Banning artist'
          Messages().menu_choice(show)
        if c == 'b':
          tr_id = current_song.split('_')[3].replace('.mp3','')
          self.ban(tr_id,1)
          show = 'Banning song'
          Messages().menu_choice(show)
        if c == 's':
          show = "Saving info to {}".format(save_file)
          Messages().menu_choice(show)
          self.save_track_info(current_song)
        if c == 'w':
          artist_url = EasyID3(os.path.join(music_dir,current_song))['website'][0]
          show = 'Opening Bandcamp page'
          Messages().menu_choice(show)
          self.browser(current_song)
    return change
