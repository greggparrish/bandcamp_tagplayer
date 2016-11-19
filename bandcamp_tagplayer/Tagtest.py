#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from clint.textui import colored, puts, progress
import configparser
import json
import os
import re
import requests
import subprocess

from db import *
from messages import Messages

config_path = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')
cache_path = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/cache/')

class Tagplayer:
  def config():
    config = configparser.ConfigParser()
    config.read(config_path+'config')
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

  def ask_for_tag(self):
    tag = input("Enter a tag: ")
    self.get_album_meta(tag, 1) 

  def existing_songs(self, tag):
    pass 

  def init_queue(tracks):
    """ queue = artist,title,album,fn,price,link,album desc """
    """ will need info from songs table, so this will happen once song is dled """
    queue = '' 

  def update_queue(queue,tracks,task):
    """ Add tracks to current queue """
    for t in tracks:
      queue += queue[[t]]
    return queue

  def get_album_meta(self, tag, page):
    """ Get albums, artists and links for a given tag, insert into db """
    while page < 11:
      r = requests.get('https://bandcamp.com/tag/{}?page={}'.format(tag, page))
      if r.status_code != 404:
        soup = BeautifulSoup(r.text, 'lxml')
        album_list = soup.find_all('li', class_='item')
        if not album_list:
          Messages.no_tag_results(tag)
          self.ask_for_tag()
        else:
          Messages.results_found(tag)
          for a in album_list:
          #need: album_name,album_url,songs,artist_name,artist_url
            al_n = a.find('div', class_='itemtext').text
            link = a.find('a')['href']
            ar_n = a.find('div', class_='itemsubtext').text
            ar_l = link.split('/album/',1)[0].replace('https://','')
            al_l = link.split('/album/')[1]
            Database.add_album(tag.strip(), al_n, al_l, ar_n, ar_l)
        if page == 1:
          page = 11
        else:
          page += 1
    self.get_track_meta(tag)

  def get_track_meta(self, tag):
    """ Grab album from db, get song url, metadata for that album """
    """ songs: artist_url, album_url,  """
    tag_id = Database.get_tag_id(tag)
    songs = Database.get_five_songs(tag_id)
    Messages.getting_track_meta(tag)
    for s in songs:
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


  def download_track(self, queue):
    path = cache_path
    path = os.path.join(cache_path, 'queue.mp3')
    r = requests.get(url, stream=url)
    with open(path, 'wb') as t:
      for chunk in r.iter_content(): 
        if chunk:
          t.write(chunk)
          t.flush()
    return path

  def play_track(self, track):
    command = "mplayer {} > /tmp/mlog.txt".format(track)
    subprocess.os.system(command)

t = Tagplayer()
Tagplayer.ask_for_tag(t)
