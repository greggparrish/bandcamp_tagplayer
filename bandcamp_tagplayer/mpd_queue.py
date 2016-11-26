#!/usr/bin/python3

from blessed import Terminal
from time import sleep

import config
from db import Database
from messages import Messages
from mpd import MPDClient
import utils

""" 
  Get config values for mpd
  set host and port
  Create symlink in music dir
  Get random state and reset to user state on tagplayer exit
"""  

cache_sym = 'cache'
save_file = config.save_file
port = 6600
host = "localhost"

class MPDConn(object):
  def __init__(self, host, path):
    self.host = host
    self.port = port
    self.client = None

  def __enter__(self):
    self.client = MPDClient()
    self.client.connect(host,port)
    # 0 is random off, 1 is on
    self.client.random(0)
    #self.client.play_state = self.client.status()['state']
    return self.client

  def __exit__(self, exc_class, exc, traceback):
    self.client.close()
    self.client.disconnect()

class MPDQueue(object):
  def add_song(song):
    with MPDConn(host,port) as m:
      m.update('cache')
      sleep(3)
      song_id = m.add(song)
      play_state = m.status()['state']
      if play_state is not 'play':
        m.play()

  def watch_playlist(self, tag):
    """
    Check playlist every 2 seconds, if under 4 tracks, get more
    """
    term = Terminal()
    with MPDConn(host,port) as m:
      change = False
      while True:
        songs_left = m.status()['playlistlength']
        with term.location(0, term.height - 1):
          with term.cbreak():
            c = term.inkey(1)
            if c == 'c':
              print(term.clear())
              change = True
              return change
              break
            if c =='q':
              show = 'Quitting'
              Messages.menu_choice(show)
              exit()
            if c == 'B':
              show = 'Banning artist'
              Messages.menu_choice(show)
            if c == 'b':
              show = 'Banning song'
              Messages.menu_choice(show)
            if c == 's':
              show = "Saving info to {}".format(save_file)
              Messages.menu_choice(show)
              filename = m.currentsong()['file']
              utils.save_track_info(filename)
            if c == 'w':
              show = 'Opening Bandcamp page'
              Messages.menu_choice(show)
              filename = m.currentsong()['file']
              utils.browser(filename)
        if int(songs_left) < 4:
          break
        else:
          self._write_status(songs_left, tag)
          sleep(2)

  def _write_status(self, songs_left, tag):
    with MPDConn(host,port) as m:
      cs = m.currentsong()
      genre = cs.get('genre', '')
      term = Terminal()
      with term.hidden_cursor():
        with term.location(0, 0):
          print(term.clear_eol+"Search tag: {}".format(tag.title()))
          print(term.clear_eol+"{} in playlist".format(songs_left))
          print(term.clear_eol+"Current song: {} by {} (genre: {})".format(cs['title'],cs['artist'], genre))
          print("[b]an song, [B]an artist, [c]hange tag, [w]ebsite, [s]ave info, [q]uit: ")
          print(term.clear_eol)
          print(term.clear_eol)

