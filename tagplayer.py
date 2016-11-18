#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests


url = 'https://lazerdiscs.bandcamp.com/album/future-dark-club'
r = requests.get(url)

soup = BeautifulSoup(r.text, "lxml")
album = {
  "tracks": [],
  "title": "",
  "artist": "",
  "art": "",
  "date": ""
}

print(album)
