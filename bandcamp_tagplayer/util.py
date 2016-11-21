#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Util:
  def format_url(url):
    """ Some artists/labels have urls without ".bandcamp.com", note these in db """
    if "bandcamp" in url:
      url = url.split('/album/',1)[0].replace('https://','').replace('.bandcamp.com','')
    else:
      url = url.split('/album/',1)[0].replace('http://','')
    return url

  def get_url(ar_l,so_l):
    if '.' in ar_l:
      url = "http://{}/track/{}".format(ar_l,so_l)
    else:
      url = "https://{}.bandcamp.com/track/{}".format(ar_l,so_l)
    return url



