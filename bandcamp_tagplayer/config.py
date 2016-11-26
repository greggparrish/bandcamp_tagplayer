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

cache_dir = format_path(conf['storage']['cache'])
save_file = format_path(conf['storage']['save_file'])
music_dir = format_path(conf['mpd']['music_dir'])
browser = conf['browser']['browser']

"""
def build_dirs(path):    
  if not os.path.exists(path):
    os.makedirs(path)
  return path
"""

