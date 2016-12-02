#!/usr/bin/python3

import sqlite3
import os

config_path = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')
songs_db =  os.path.join(config_path, 'bans.db')

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
    self._create_table()

  def _create_table(self):
    with dbconn(songs_db) as c:
      c.execute('CREATE TABLE IF NOT EXISTS bans (item_id INTEGER UNIQUE, item_type INTEGER)')

  def check_ban(item_id, item_type):
    """ Check if album or song has been banned """
    with dbconn(songs_db) as c:
      ban = c.execute("SELECT item_id FROM bans WHERE item_id = ? AND item_type = ?", (item_id,item_type)).fetchone()
    return ban

  def ban_item(item_id, item_type):
    """ Ban an album or song. id from filename, 
        item_type:  0 = album, 1 = song """
    with dbconn(songs_db) as c:
      banned = c.execute("INSERT OR IGNORE INTO bans (item_id,item_type) VALUES (?,?)", (item_id,item_type))
    return banned
