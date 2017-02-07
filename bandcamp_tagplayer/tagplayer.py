#!/usr/bin/python3

import json
import os
import random
from random import randint
import re
import time
from time import sleep

from blessed import Terminal
from bs4 import BeautifulSoup
from clint.textui import progress
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3
import requests
from slugify import slugify

from config import Config
import db
from mpd_queue import MPDQueue
from messages import Messages
from utils import Utils

c = Config().conf_vars()


class Tagplayer:
  def __init__(self):
    ut = Utils()
    ut.symlink_musicdir()
    ut.clear_cache()
    MPDQueue().update_mpd()

  def ask_for_tag(self):
    term = Terminal()
    print(term.clear())
    tag = input("Enter a tag: ")
    tag = slugify(tag)
    self.monitor_mpd(tag)

  def monitor_mpd(self, tag):
    change = MPDQueue().watch_playlist(tag)
    if change == True:
      self.ask_for_tag()
    else:
      self.get_albums(tag)

  def get_albums(self, tag):
    """ Get album urls """
    page = randint(1, 10)
    sort = random.choice(['pop', 'new'])
    try:
      r = requests.get('https://bandcamp.com/tag/{}?page={}?sort_field={}'.format(tag, page, sort))
    except requests.exceptions.RequestException as e:
      print(e)
      exit()
    if r.status_code != 404:
      Messages().results_found(tag)
      soup = BeautifulSoup(r.text, 'lxml')
      album_list = soup.find_all('li', class_='item')
      tags = soup.find_all('a', class_='related_tag')
      tag_list = ', '.join([t.text for t in tags])
      Messages().related_tags(tag_list)
      if not album_list:
        Messages().no_tag_results(tag)
        sleep(1)
        self.ask_for_tag()
      else:
        albums = []
        for a in album_list:
          albums.append([a.find('a')['href']])
    self.get_song_meta(albums, tag)

  def get_song_meta(self, albums, tag):
    """ Choose random song from album,
    get metadata (artist, title, album, url, date, dl_url for that song """
    r_albums = random.sample(albums, 4)
    for a in r_albums:
      url = a[0]
      try:
        r = requests.get(url)
      except requests.exceptions.RequestException as e:
        print(e)
      if r.status_code != 404:
        soup = BeautifulSoup(r.text, 'lxml')
        """ check if song is tagged with anything from banlist """
        tags = soup.find_all('a', class_='tag')
        tag_list = []
        for t in tags:
          tag_list.append(str(t))
        if len([x for x in tag_list if x in c['banned_genres']]) == 0:
          """ album meta from bs4 & current: """
          artist = soup.find('span', itemprop='byArtist')
          artist = artist.find('a').text
          bc_meta = re.search('current\: (.*?)},', r.text).group(1)
          m_json = json.loads(bc_meta+'}')
          date = re.search('\d{4}', str(m_json['release_date'])).group(0)
          """ song meta from trackinfo: """
          songs = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
          s_json = json.loads("["+songs+"]")
          s = random.choice(s_json)

          if s['file'] != None:
            metadata = {
              'artist': artist,
              'artist_id': str(m_json['band_id']),
              'track': s['title'],
              'track_id': str(s['track_id']),
              'album': m_json['title'],
              'date': date,
              'album_url': url,
              'dl_url': s['file']['mp3-128'],
              'genre': tag,
            }
            ar_check = db.Database.check_ban(metadata['artist_id'],0)
            tr_check = db.Database.check_ban(metadata['track_id'],0)
            if not ar_check or not tr_check:
              self.download_song(metadata, tag)
    self.monitor_mpd(tag)

  def download_song(self, metadata, tag):
    dl_url = 'http:'+metadata['dl_url']
    timestamp = int(time.time())
    fn = ['bctcache', str(timestamp), metadata['artist_id'], metadata['track_id']]
    filename = '_'.join(fn)+'.mp3'
    path = os.path.join(c['cache_dir'], filename)
    """ If exists, load, if not dl """
    rel_path = c['cache_dir'].split('/')[-1]
    local_path = rel_path+'/'+filename
    if os.path.isfile(path) is True:
      MPDQueue.add_song(local_path)
    else:
      try:
        r = requests.get(dl_url, stream=dl_url)
      except requests.exceptions.RequestException as e:
        print(e)
        quit()
      Messages().now_loading(metadata['artist'], metadata['track'])
      with open(path, 'wb') as t:
        total_length = int(r.headers.get('content-length', 0))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
          if chunk:
            t.write(chunk)
            t.flush()
      self.write_ID3_tags(filename,metadata)
      MPDQueue().add_song(local_path)

  def write_ID3_tags(self, filename, metadata):
    path = os.path.join(c['cache_dir'], filename)
    try:
      song = EasyID3(path)
    except ID3NoHeaderError:
      song = File(path, easy=True)
    song['title'] = metadata['track']
    song['artist'] = metadata['artist']
    songdd = 22
    song['album'] = metadata['album']
    song['genre'] = metadata['genre'].title().replace('-',' ')
    song['date'] = metadata['date']
    song['website'] = metadata['album_url']
    song.save()
