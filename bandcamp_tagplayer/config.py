#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import configparser

ConfigPath = os.path.join(os.path.expanduser('~'), '.config/bandcamp_tagplayer/')

""" read or create config file """
conf = configparser.ConfigParser()
conf.read(ConfigPath+'config')

cache_dir = conf['storage']['cache']
save_dir = conf['storage']['save']

if '~' in cache_dir:
  cache_dir = os.path.expanduser(cache_dir)
if not os.path.exists(cache_dir):
  os.makedirs(cache_dir)
