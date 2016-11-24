#!/usr/bin/python3
# -*- coding: utf-8 -*-

from clint.textui import colored, puts

class Messages:
  def creating_db():
    print(colored.green("Creating database"))

  def current_song(song):
    print("Now playing: {} by {} from {}".format(song.name, song.artist, song.album))

  def idle():
    print(colored.green("Idle. Waiting until playlist is < 4."))

  def no_tag_results(tag):
    print(colored.red("No results for tag: "), colored.green("{}".format(tag)))

  def now_loading(artist, track):
    print(colored.red("Now loading: {} by {}".format(track, artist)))

  def results_found(tag):
    print(colored.green("Downloading metadata for {} albums".format(tag)))

  def related_tags(tags):
    print(colored.green("Related tags: "),colored.red("{}").format(tags))
