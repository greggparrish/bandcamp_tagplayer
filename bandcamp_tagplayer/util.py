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

  def get_url(ar_l,so_l,linktype):
    if '.' in ar_l:
      url = "http://{}/{}/{}".format(ar_l,linktype,so_l)
    else:
      url = "https://{}.bandcamp.com/{}/{}".format(ar_l,linktype,so_l)
    return url
