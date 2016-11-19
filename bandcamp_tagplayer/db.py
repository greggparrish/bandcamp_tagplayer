#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import os

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
    with dbconn('./songs.db') as c:
      self._create_table()

  def _create_table(self):
    """ Create db tables if they don't already exist.  One for artists, albums, tags, songs, queue and a M2M table for album tags.  """
    c.execute('CREATE TABLE IF NOT EXISTS artists (artist_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS albums (album_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT UNIQUE, artist_id INTEGER, FOREIGN KEY (artist_id) REFERENCES artists (artist_id) ON DELETE CASCADE ON UPDATE NO ACTION)')
    c.execute('CREATE TABLE IF NOT EXISTS songs (song_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url text UNIQUE, album_id INTEGER, love INTEGER, ban INTEGER, plays INTEGER, saved INTEGER, FOREIGN KEY (album_id) REFERENCES albums (album_id) ON DELETE CASCADE ON UPDATE NO ACTION)')
    c.execute('CREATE TABLE IF NOT EXISTS tags (tag_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS album_tags (album_tag_id INTEGER PRIMARY KEY AUTOINCREMENT, album_id INTEGER, tag_id INTEGER, FOREIGN KEY (album_id) REFERENCES albums (album_id) ON DELETE CASCADE ON UPDATE NO ACTION, FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE ON UPDATE NO ACTION, UNIQUE (album_id, tag_id))')
    conn.commit()
    conn.close()

  def add_album(tag,al_n,al_l,ar_n,ar_l):
    """ Add album, artist, tag and song info to db """
    with dbconn(songs_db) as c:
      c.execute("INSERT OR IGNORE INTO artists(name,url) VALUES(?,?)", (ar_n, ar_l))
      artist_id = c.execute("SELECT artist_id from artists where url = ?", (ar_l,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO albums(name,url,artist_id) VALUES(?,?,?)", (al_n,al_l,artist_id))
      album_id = c.execute("SELECT album_id from albums where url = ?", (al_l,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
      tag_id = c.execute("SELECT tag_id from tags where name = ?", (tag,)).fetchone()[0]
      c.execute("INSERT OR IGNORE INTO album_tags(tag_id,album_id) VALUES(?,?)", (tag_id,album_id))

  def add_song(al_id,s_n,s_l):
    with dbconn(songs_db) as c:
      c.execute("INSERT OR IGNORE INTO songs(name,url,album_id) VALUES(?,?,?)", (s_n,s_l,al_id))

  def get_tag_id(tag): 
    with dbconn(songs_db) as c:
      tag_id = c.execute("SELECT tag_id from tags where name = ?", (tag,)).fetchone()[0]
      return tag_id

  def get_five_songs(tag_id):
    """ Get 5 songs with chosen tag for download """
    with dbconn(songs_db) as c:
      songs = c.execute("SELECT artists.url AS ar_u, songs.url AS tr_l, songs.name AS tr_n, album.url AS al_u LIMIT 5").fetchall()

  def tagged_albums(tag_id):
    """ Get album urls with chosen tag """
    with dbconn(songs_db) as c:
      albums = c.execute("SELECT artists.url AS ar_l, albums.url AS al_l, albums.album_id as al_id FROM albums INNER JOIN artists ON albums.artist_id = artists.artist_id INNER JOIN album_tags ON albums.album_id = album_tags.album_id WHERE album_tags.tag_id = ?", (tag_id,)).fetchall()
      return albums
