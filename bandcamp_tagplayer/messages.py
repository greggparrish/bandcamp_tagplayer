#!/usr/bin/python3
# -*- coding: utf-8 -*-

from clint.textui import colored, puts

class Messages:
  def current_track(track):
    print("Now playing: {} by {} from {}".format(track.name, track.artist, track.album))

  def no_tag_results(tag):
    print(colored.red("No results for tag: "), colored.green("{}".format(tag)))

  def results_found(tag):
    print(colored.green("Downloading metadata for {} albums".format(tag)))

  def getting_track_meta(tag):
    print(colored.green("Downloading track info"))

  def downloading_tracks(tag):
    print(colored.green("Downloading tracks"))
