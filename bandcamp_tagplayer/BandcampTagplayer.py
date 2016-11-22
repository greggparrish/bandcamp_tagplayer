#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
  TODO: 
    - fix update album data loop
    - When to pull from tagged songs vs albums, how to balance newer tracks vs pulling from db
    - url in comments
    - rm playcount, download from songs 
    - symlink cache dir to mpd music_dir
    - be able to hot key open current track in browser
    - arg to rebuild db
    - add year to metadata
    - turn mpd random on/off through ui
    - first album grab get popular (?sort_field=pop), second or update get new(?sort_field=date)
    - set number to add to playlist in conf, use in db
"""

from bs4 import BeautifulSoup
from clint.textui import progress
import json
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, COMM, ID3NoHeaderError
from mutagen.easyid3 import EasyID3
import os
import random
import re
import requests
from slugify import slugify
import subprocess

import config
import db
from util import Util as util
from messages import Messages
from mpd_queue import MPDQueue

db = db.Database
cache_dir = config.cache_dir
save_dir = config.save_dir

class Tagplayer:
  def __init__(self):
    db()

  def ask_for_tag(self):
    tag = input("Enter a tag: ")
    self.existing_songs(tag.lower())

  def existing_songs(self, tag):
    tag = slugify(tag)
    tag_id = db.get_tag_id(tag)
    albums = db.tagged_albums(tag_id) 
    if len(albums) > 5:
      self.get_song_meta(tag, tag_id, albums)
    else: 
      self.get_album_meta(tag, 1) 

  def get_album_meta(self, tag, page):
    """ Get albums, artists and links for a given tag, insert into db """
    sort = 'pop' if page is 1 else 'date'
    r = requests.get('https://bandcamp.com/tag/{}?page={}?sort_field={}'.format(tag, page, sort))
    if r.status_code != 404:
      Messages.results_found(tag)
      soup = BeautifulSoup(r.text, 'lxml')
      album_list = soup.find_all('li', class_='item')
      tags = soup.find_all('a', class_='related_tag')
      tag_list = ', '.join([t.text for t in tags])
      Messages.related_tags(tag_list)
      if not album_list:
        Messages.no_tag_results(tag)
        self.ask_for_tag()
      else:
        albums = []
        for a in album_list:
          al_n = a.find('div', class_='itemtext').text
          link = a.find('a')['href']
          ar_n = a.find('div', class_='itemsubtext').text
          ar_l = util.format_url(link) 
          al_l = link.split('/album/')[1]
          tag_id,al_id = db.add_album(tag.strip(), al_n, al_l, ar_n, ar_l)
          albums += [[ar_l,al_l,al_id]]
  self.get_song_meta(tag, tag_id, None)

  def get_song_meta(self, tag, tag_id, albums):
    """ Choose random song from album, get metadata for that song """
    Messages.getting_song_meta(tag)
    print(albums)
    if albums == None:
      albums = db.tagged_albums(tag_id) 
    for a in albums:
      url = util.get_url(a[0],a[1],'album') 
      print(url)
      r = requests.get(url)
      if r.status_code != 404:
        songs = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
        songs_j = json.loads("["+songs+"]")
        s = random.choice(songs_j)
        s['title_link'] = "" if s['title_link'] is None else s['title_link']
        db.add_song(a[2], s['title'], s['title_link'].replace('/track/',''))
      else:
        pass
    self.download_song(tag_id, tag)

  def download_song(self, tag_id, tag):
    songs = db.get_songs(tag_id)
    Messages.loading_cache()
    print(len(songs))
    for s in songs:
      song_url = util.get_url(s[0],s[1], 'track') 
      dl_url = self.get_mp3_url(song_url, s[6])
      metadata = {
        'artist': s[3],
        'so_title': s[4],
        'album': s[5],
        'song_url': song_url,
        'genre': tag,
        'comment': song_url
      }
      filename = slugify(metadata['artist'])+'_'+slugify(metadata['so_title'])+'.mp3'
      path = os.path.join(cache_dir, filename)
      """ If exists, load, if not dl """
      if os.path.isfile(path) is True:
        song = cache_dir.split('/')[-1]+'/'+filename 
        print(song)
        MPDQueue.add_song(song)
      else:
        r = requests.get(dl_url, stream=dl_url)
        print("Now loading: {} by {}".format(metadata['so_title'],metadata['artist']))
        with open(path, 'wb') as t:
          total_length = int(r.headers.get('content-length', 0))
          for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
              t.write(chunk)
              t.flush()
        song = cache_dir.split('/')[-1]+'/'+filename 
        print(song)
        self.write_ID3_tags(filename,metadata)
        MPDQueue.add_song(song)
    MPDQueue.watch_playlist(tag)

  def get_mp3_url(self,song_page,song_id):
    r = requests.get(song_page)
    if r.status_code != 404:
      meta = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
      mj = json.loads("["+meta+"]")
      if mj[0]['file'] is None:
        """ No file available so ban song """
        db.ban_song(song_id)
      else:
        dl_url = "http:"+mj[0]['file']['mp3-128']
      return dl_url

  def write_ID3_tags(self, filename, metadata):
    Messages.writing_metadata(metadata['so_title'], metadata['artist'])
    path = os.path.join(cache_dir, filename)
    song = MP3(path)
    #song['COMM'] = COMM(encoding=3, text=metadata['comment'], lang='eng')
    song.save()
    try:
      song = EasyID3(path)
    except ID3NoHeaderError:
      song = File(path, easy=True)
    song['title'] = metadata['so_title']
    song['artist'] = metadata['artist']
    song['album'] = metadata['album']
    song['genre'] = metadata['genre'].title().replace('-','')
    song.save()

t = Tagplayer()
Tagplayer.ask_for_tag(t)
