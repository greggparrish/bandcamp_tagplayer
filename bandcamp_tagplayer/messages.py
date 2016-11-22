#!/usr/bin/python3
# -*- coding: utf-8 -*-

from clint.textui import colored, puts

class Messages:
  def creating_db():
    print(colored.green("Creating database"))

  def current_song(song):
    print("Now playing: {} by {} from {}".format(song.name, song.artist, song.album))

  def downloading_songs(tag):
    print(colored.green("Downloading songs"))

  def getting_song_meta(tag):
    print(colored.green("Downloading song metadata"))

  def loading_cache():
    print(colored.green("Loading cache"))

  def no_tag_results(tag):
    print(colored.red("No results for tag: "), colored.green("{}".format(tag)))

  def results_found(tag):
    print(colored.green("Downloading metadata for {} albums".format(tag)))

  def writing_metadata(song, artist):
    print(colored.green("Writing metadata for {} by {}".format(song, artist)))

  def related_tags(tags):
    print(colored.green("Related tags: "),colored.red("{}").format(tags))
