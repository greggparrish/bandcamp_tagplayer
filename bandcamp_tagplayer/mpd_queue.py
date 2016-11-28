#!/usr/bin/python3

from blessed import Terminal
from time import sleep

import config
from db import Database
from mpd import MPDClient
from utils import Utils

""" 
  set host and port
  Create symlink in music dir
"""  

cache_sym = 'cache'
save_file = config.save_file
mpd_host = config.mpd_host
mpd_port = config.mpd_port

class MPDConn(object):
  def __init__(self, host, path):
    self.host = mpd_host
    self.port = mpd_port
    self.client = None
    d = Database()

  def __enter__(self):
    self.client = MPDClient()
    self.client.connect(mpd_host,mpd_port)
    # 0 is random off, 1 is on
    #self.client.random(0)
    return self.client

  def __exit__(self, exc_class, exc, traceback):
    self.client.close()
    self.client.disconnect()

class MPDQueue(object):
  def add_song(song):
    with MPDConn(mpd_host,mpd_port) as m:
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
    print(term.clear())
    with MPDConn(mpd_host,mpd_port) as m:
      change = False
      while True:
        songs_left = m.status()['playlistlength']
        try:
          curr_song = m.currentsong()['file']
        except:
          break
        change = Utils().options_menu(curr_song)
        if int(songs_left) < 4 or change is True:
          break
        else:
          self._write_status(songs_left, tag)
          sleep(2)
    return change

  def _write_status(self, songs_left, tag):
    with MPDConn(mpd_host,mpd_port) as m:
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

