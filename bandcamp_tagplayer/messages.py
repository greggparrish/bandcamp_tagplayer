#!/usr/bin/python3

from blessed import Terminal
from time import sleep

class Messages:
  def creating_db(self):
    print("Creating database")

  def current_song(self, song):
    print("Now playing: {} by {} from {}".format(song.name, song.artist, song.album))

  def menu_choice(self, show):
    term = Terminal()
    print(term.clear())
    print(show)
    sleep(1)
    print(term.clear())

  def no_tag_results(self, tag):
    print("No results for tag: {}".format(tag))

  def now_loading(self, artist, track):
    print("Now loading: {} by {}".format(track, artist))

  def results_found(self, tag):
    print("Downloading metadata for {} albums".format(tag))

  def related_tags(self, tags):
    term = Terminal()
    print(term.bold+"Related tags: {}".format(tags)+term.normal)
