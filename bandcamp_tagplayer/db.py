#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from messages import Messages

config_path = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')
songs_db =  os.path.join(config_path, 'songs.db')

class dbconn(object):
    """ DB context manager """
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()

class Database:
  def __init__(self):
    with dbconn(songs_db) as c:
      tables = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
      if tables < 6:
        self._create_table()

  def _create_table(self):
    Messages.creating_db()
    with dbconn(songs_db) as c:
      """ Create db tables if they don't already exist.  One for artists, albums, tags, songs and a M2M table for album tags.  """
      c.execute('CREATE TABLE IF NOT EXISTS artists (artist_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT UNIQUE)')
      c.execute('CREATE TABLE IF NOT EXISTS albums (album_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT UNIQUE, artist_id INTEGER, FOREIGN KEY (artist_id) REFERENCES artists (artist_id) ON DELETE CASCADE ON UPDATE NO ACTION)')
      c.execute('CREATE TABLE IF NOT EXISTS songs (song_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url text UNIQUE, album_id INTEGER, ban INTEGER, FOREIGN KEY (album_id) REFERENCES albums (album_id) ON DELETE CASCADE ON UPDATE NO ACTION)')
      c.execute('CREATE TABLE IF NOT EXISTS tags (tag_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
      c.execute('CREATE TABLE IF NOT EXISTS album_tags (album_tag_id INTEGER PRIMARY KEY AUTOINCREMENT, album_id INTEGER, tag_id INTEGER, FOREIGN KEY (album_id) REFERENCES albums (album_id) ON DELETE CASCADE ON UPDATE NO ACTION, FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE ON UPDATE NO ACTION, UNIQUE (album_id, tag_id))')

  def get_all_tags():
    with dbconn(songs_db) as c:
      tags = c.execute("SELECT name FROM tags").fetchall()
      return tags

  def add_album(tag,al_n,al_l,ar_n,ar_l):
    """ Add album, artist, tag and song info to db """
    with dbconn(songs_db) as c:
      c.execute("INSERT OR IGNORE INTO artists(name,url) VALUES(?,?)", (ar_n, ar_l))
      ar_id = c.execute("SELECT artist_id from artists where url = ?", (ar_l,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO albums(name,url,artist_id) VALUES(?,?,?)", (al_n,al_l,ar_id))
      al_id = c.execute("SELECT album_id from albums where url = ?", (al_l,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
      t_id = c.execute("SELECT tag_id from tags where name = ?", (tag,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO album_tags(tag_id,album_id) VALUES(?,?)", (t_id,al_id))
      return t_id, al_id

  def add_song(al_id,s_n,s_l):
    with dbconn(songs_db) as c:
      song = c.execute("INSERT OR IGNORE INTO songs(name,url,album_id) VALUES(?,?,?)", (s_n,s_l,al_id))
      return song

  def ban_song(song_id):
    with dbconn(songs_db) as c:
      song = c.execute("UPDATE songs SET ban = '1' WHERE song_id = ?", (song_id))
      return song

  def get_tag_id(tag):
    with dbconn(songs_db) as c:
      check_tag = c.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
      tag_id = c.execute("SELECT tag_id from tags where name = ?", (tag,)).fetchone()[0]
      return tag_id

  def get_songs(tag_id):
    """ Get 5 songs with chosen tag for download: artist url, song url, album url, artist name, song title, album title, song_id """
    with dbconn(songs_db) as c:
      songs = c.execute("SELECT artists.url, songs.url, albums.url, artists.name, songs.name, albums.name, songs.song_id FROM albums INNER JOIN artists ON albums.artist_id = artists.artist_id INNER JOIN songs ON songs.album_id = albums.album_id INNER JOIN album_tags ON album_tags.album_id = albums.album_id WHERE album_tags.tag_id = ? AND songs.ban IS NOT '1' ORDER BY RANDOM() LIMIT 2", (tag_id,)).fetchall()
      return songs

  def download_status(song_id,status):
    """ Change download status for song: 1 = downloaded, 0 = not """
    with dbconn(songs_db) as c:
      status = c.execute("UPDATE songs SET downloaded=? where song_id = ?", (status, song_id))
      return status

  def tagged_albums(tag_id):
    """ Get album urls with chosen tag """
    with dbconn(songs_db) as c:
      albums = c.execute("SELECT artists.url, albums.url, albums.album_id FROM albums INNER JOIN artists ON albums.artist_id = artists.artist_id INNER JOIN album_tags ON albums.album_id = album_tags.album_id WHERE album_tags.tag_id = ? ORDER BY RANDOM() LIMIT 6", (tag_id,)).fetchall()
      return albums


