#!/usr/bin/python3
# -*- coding: utf-8 -*-

from blessed import Terminal
from messages import Messages
from mpd import MPDClient
from time import sleep

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

class MPDQueue(object):
  def add_song(song):
    with MPDConn(host,port) as m:
      m.update('cache')
      sleep(3)
      song_id = m.add(song)
      play_state = m.status()['state']
      if play_state is not 'play':
        m.play()

  def _check_playlist(self):
    with MPDConn(host,port) as m:
      songs_left = m.status()['playlistlength']
    return songs_left

  def watch_playlist(self, tag):
    """
    Check playlist every 2 seconds, if under 4, get more
    """
    with MPDConn(host,port) as m:
      while True:
        songs_left = self._check_playlist()
        if songs_left < '4':
          break
        else:
          self._write_status(songs_left, tag)
          sleep(2)

  def _write_status(self, songs_left, tag):
    with MPDConn(host,port) as m:
      cs = m.currentsong()
      term = Terminal()
      print(term.clear())
      with term.hidden_cursor():
        with term.location(0, term.height - 6):
          print("Tag: {}".format(tag.title()))
          print("Current song: {} by {} (genre: {})".format(cs['title'],cs['artist'],cs['genre']))
          print("{} in playlist".format(songs_left))
          print("[b]an song, [B]an album, [c]hange tag, [q]uit:")

#m = MPDQueue()
#m.watch_playlist()
