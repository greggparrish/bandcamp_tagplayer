#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import sleep
from mpd import MPDClient

""" 
  Get config values for mpd
  set host and port
  Create symlink in music dir
  Get random state and reset to user state on tagplayer exit
"""  
cache_sym = 'cache'
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

class MPDQueue:
  def add_song(song, tag):
    with MPDConn(host,port) as m:
      m.update('cache')
      sleep(3)
      song_id = m.add(song)
      play_state = m.status()['state']
      if play_state is not 'play':
        m.play()

  def watch_playlist(tag):
    """
    TODO: Check playlist.  When < 5, reload cache
    """
    with MPDConn(host,port) as m:
      while True:
        if songs_left < '4':
          break
          #self.get_album_meta(tag, 1) 
          #def get_album_meta(self, tag, page):
        else:
          sleep(2)

