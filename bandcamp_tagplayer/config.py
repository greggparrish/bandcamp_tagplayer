#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import configparser

ConfigPath = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')

""" read or create config file """
conf = configparser.ConfigParser()
conf.read(ConfigPath+'config')

def format_path(path):
  if '~' in path:
    path = os.path.expanduser(path)
  else:
    path = path
  return path

browser = conf['browser']['browser']
cache_dir = format_path(conf['storage']['cache'])
mpd_host = conf['mpd']['host']
mpd_port = conf['mpd']['port']
music_dir = format_path(conf['mpd']['music_dir'])
save_file = format_path(conf['storage']['save_file'])


