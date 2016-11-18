#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import json
import os
import re
import requests

from db import *

ConfigPath = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')

def config():
  config = configparser.ConfigParser()
  config.read(ConfigPath+'config')
  cache_dir = config['cache']['save_to']
  if '~' in cache_dir:
    cache_dir = os.path.expanduser(cache_dir)
  return cache_dir

def create_cache_dir():
  sd = config()
  cache_dir = os.path.join(sd, 'tagplayer_cache')
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
  return cache_dir

def get_urls():
  """
  Get albums, artists and links for a given tag, insert into db
  """
  tag = 'darkwave'
  page_no = 1
  while page_no < 11:
    r = requests.get('https://bandcamp.com/tag/{}?page={}'.format(tag, page_no))
    if r.status_code != 404:
      soup = BeautifulSoup(r.text, 'lxml')
      album_list = soup.find_all('li', class_='item')
      for a in album_list:
      #need: album_name,album_url,songs,artist_name,artist_url
        al_n = a.find('div', class_='itemtext').text
        link = a.find('a')['href']
        ar_n = a.find('div', class_='itemsubtext').text
        ar_l = link.split('/album/',1)[0].replace('https://','')
        al_l = link.split('/album/')[1]
        Database.add_album(tag.strip(), al_n, al_l, ar_n, ar_l)
      page_no += 1

def pop_queue(tag):
  """
  Grab album from db, get song url, metadata for that album
  """
  tag_id = Database.get_tag_id(tag)
  albums = Database.tagged_albums(tag_id)
  for a in albums:
    url = "https://{}/album/{}".format(a[0],a[1])
    r = requests.get(url)
    try:
      songs = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
    except:
      pass
    songs_j = json.loads("["+songs+"]")
    for s in songs_j:
      s['title_link'] = "" if s['title_link'] is None else s['title_link']
      Database.add_song(a[2], s['title'], s['title_link'].replace('/track/',''))

#Database()
#albums = get_urls()
pop_queue("darkwave")

## TODO: crawl, get album/artist/song info, plug into db, start playing file


