#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
  TODO:
    - always get random page, switch between pop and new
    - if mpd playing, get genre, ask if want more
    - symlink cache dir to mpd music_dir
    - arg to rebuild db
    - turn mpd random on/off through ui
    - clean cache
    - first album grab get popular (?sort_field=pop)
    - second or update get new(?sort_field=date)
    - set number to add to playlist in conf, use in db
    - rm unused messages
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
from random import randint
import re
import requests
from slugify import slugify
import subprocess

import config
import db
from mpd_queue import MPDQueue
from messages import Messages

db = db.Database
cache_dir = config.cache_dir
save_dir = config.save_dir


class Tagplayer:
  def __init__(self):
    d = db()

  def ask_for_tag(self):
    tag = input("Enter a tag: ")
    tag = slugify(tag)
    self.get_album_meta(tag)

  def get_album_meta(self, tag):
    """ Get album urls """
    page = randint(0, 10)
    sort = random.choice(['pop','new'])
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
          album_link = a.find('a')['href']
          albums += [[album_link]]
    self.get_song_meta(albums, tag)

  def get_song_meta(self, albums, tag):
    """ Choose random song from album,
    get metadata (artist, title, album, price, date, dl_url for that song """
    Messages.getting_song_meta(tag)
    r_albums = random.sample(albums, 3)
    for a in r_albums:
      url = a[0]
      r = requests.get(url)
      if r.status_code != 404:
        """ price """
        soup = BeautifulSoup(r.text, 'lxml')
        try:
          pricebox = soup.find('li', class_='buyItem')
          pricebox_h4 = pricebox.find('h4')
          price = pricebox_h4.find('span', class_='base-text-color').text
          currency = pricebox_h4.find('span', class_='buyItemExtra secondaryText').text
        except:
          price = currency = ''

        """ album meta """
        artist = soup.find('span', itemprop='byArtist')
        artist = artist.find('a').text
        album_title = soup.find('h2', class_='trackTitle').text

        date = soup.find('div', class_='tralbum-credits').text
        date = re.search('\d{4}', date).group(0)
        """ song meta from trackinfo """
        songs = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
        songs_j = json.loads("["+songs+"]")
        s = random.choice(songs_j)

        if s['file']['mp3-128']:
          metadata = {
            'artist': artist.strip(),
            'track': s['title'],
            'album': album_title.strip(),
            'price': price,
            'currency': currency,
            'date': date,
            'album_url': url,
            'dl_url': s['file']['mp3-128'],
            'genre': tag,
          }
          self.download_song(metadata, tag)
    MPDQueue.watch_playlist()
    page = randint(0, 10)
    self.get_album_meta(tag)

  def download_song(self, metadata, tag):
    dl_url = 'http:'+metadata['dl_url']
    filename = slugify(metadata['artist'])+'_'+slugify(metadata['track'])+'.mp3'
    path = os.path.join(cache_dir, filename)
    """ If exists, load, if not dl """
    rel_path = cache_dir.split('/')[-1]+'/'+filename
    if os.path.isfile(path) is True:
      MPDQueue.add_song(rel_path)
    else:
      r = requests.get(dl_url, stream=dl_url)
      Messages.now_loading(metadata['artist'], metadata['track'])
      with open(path, 'wb') as t:
        total_length = int(r.headers.get('content-length', 0))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
          if chunk:
            t.write(chunk)
            t.flush()
      self.write_ID3_tags(filename,metadata)
      MPDQueue.add_song(rel_path)

  def write_ID3_tags(self, filename, metadata):
    path = os.path.join(cache_dir, filename)
    try:
      song = EasyID3(path)
    except ID3NoHeaderError:
      song = File(path, easy=True)
    song['title'] = metadata['track']
    song['artist'] = metadata['artist']
    song['album'] = metadata['album']
    song['genre'] = metadata['genre'].title().replace('-',' ')
    song['date'] = metadata['date']
    song['website'] = metadata['album_url']
    song.save()

t = Tagplayer()
Tagplayer.ask_for_tag(t)
