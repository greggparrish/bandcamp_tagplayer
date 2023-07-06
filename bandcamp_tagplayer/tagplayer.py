import datetime
import json
import os
import random
import re
import requests
import sys
from time import sleep, time

from blessed import Terminal
from bs4 import BeautifulSoup
from clint.textui import progress
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from .config import Config
from . import db
from .mpd_queue import MPDQueue
from .messages import msg_now_loading, msg_related_tags, msg_results_found, msg_few_tag_results, msg_missing_music_dir, msg_update_error, msg_connection_error
from .utils import Utils

c = Config().conf_vars()
BANNED_GENRES = [g.lower().strip() for g in c['banned_genres'].split(',')]
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}


class Tagplayer:

    def __init__(self, tags=None, user=None):
        self.has_more = None
        self.hub_url = 'https://bandcamp.com/api/hub/2/dig_deeper'
        self.metadata = {}
        self.page = 1
        self.page_limit = None
        self.related_tags = []
        self.tags = tags
        self.user = user
        self.user_collection = []

    def __enter__(self):
        """ Symlink mpd dir, clear out old downloads, update MPD """
        ut = Utils()
        try:
            ut.symlink_musicdir()
        except:
            msg_missing_music_dir(c["music_dir"])
            sys.exit()
        ut.clear_cache()
        db.Database()
        try:
            MPDQueue().update_mpd()
        except Exception as e:
            msg_update_error(e)
            sys.exit()
        return self

    def __exit__(self, exc_class, exc, traceback):
        if exc:
            return False
        else:
            return True

    def ask_for_tag(self):
        """ If started without tag or user changed tag through menu, get and slugify tag """
        while True:
            term = Terminal()
            print(term.clear())
            tag = input("Enter genre(s): ")
            if tag:
                tags = re.sub(',', ' ', tag)
                self.tags = re.sub(' +', ' ', tags).split(' ')
                break
        self.check_tag()

    def ask_for_user(self):
        """ Get a username to stream their collection """
        while True:
            term = Terminal()
            print(term.clear())
            username = input("Enter a username: ")
            if username:
                self.user = username
                break
            else:
                continue
        self.get_user_collection()

    def get_user_collection(self):
        """ Hit API to get all tracks bought by a given user.  Store to self.user_collection.  """
        self.user = re.split('/', self.user)[-1] if '/' in self.user else self.user
        user_url = f'https://bandcamp.com/{self.user}'
        user_page = requests.get(user_url, headers=HEADERS)
        if user_page.status_code != requests.codes.ok:
            print(f'User {self.user} does not appear to be a valid user.')
            sys.exit()
        soup = BeautifulSoup(user_page.content, 'lxml')
        pagedata = soup.find('div', id='pagedata')
        if not pagedata:
            print(f'User page for {self.user} missing data.')
            sys.exit()
        pj = json.loads(pagedata.get('data-blob'))
        collection_count = pj.get('current_fan', 0).get('collection_count', 0)
        fan_id = pj.get('fan_data').get('fan_id')
        last_token = pj.get('collection_data').get('last_token')
        self.parse_tracks(pj, page=True)
        cc = 0 if collection_count <= 45 else collection_count
        print(f'Found {cc} tracks for {self.user}')
        while cc > 0:
            print(f'Getting collection data: {cc} tracks left')
            post_data = {'fan_id': fan_id, 'older_than_token': last_token, 'count': 40}
            user_api_url = 'https://bandcamp.com/api/fancollection/1/collection_items'
            r = requests.post(user_api_url, json=post_data, headers=HEADERS)
            np = r.json()
            self.parse_tracks(np, api=True)
            cc -= 40
        self.monitor_mpd()

    def parse_tracks(self, tracks, page=None, api=None):
        """ Get track data from API response, load into self.user_collection """
        if page:
            tl = tracks.get('item_cache').get('collection')
            new_tracks = [{'item_id': tl[t]['item_id'], 'item_url': tl[t]['item_url'],
                           'tralbum_type': tl[t]['tralbum_type']} for t in tl]
        else:
            tl = tracks.get('items')
            new_tracks = [{'item_id': t['item_id'], 'item_url': t['item_url'],
                           'tralbum_type': t['tralbum_type']} for t in tl]
        self.user_collection += new_tracks
        return True

    def no_results(self):
        """ Prints no results msg to terminal, asks for a new tag """
        msg_no_tag_results(self.tags)
        sleep(1)
        self.ask_for_tag()

    def check_tag(self):
        """
          Verify that a tag has albums, and get the number of pages of the results.
          More obscure genres might only have a few albums, so we need the number of
          pages to randomize within page limits.
        """
        if self.user:
            self.get_user_collection()
            return
        elif not self.tags and not self.user:
            self.ask_for_tag()
        elif not set(self.tags).isdisjoint(BANNED_GENRES):
            print(f'\nTag banned in your config file.\nEither remove it from your ban_list or choose another tag.')
            sleep(2)
            self.ask_for_tag()
        else:
            hub_data = {"filters": {"format": "all", "location": 0, "sort": "new", "tags": self.tags}, "page": "1"}
            try:
                r = requests.post(self.hub_url, json=hub_data, headers=HEADERS)
            except Exception:
                self.no_results()
            if not r:
                self.no_results()
            res = r.json()
            tracks = res.get('items', None)
            self.has_more = res.get('more_available', None)

            if tracks and len(tracks) > 2:
                self.monitor_mpd()
            else:
                self.no_results()

    def monitor_mpd(self):
        """
          Keep watch of the  number of songs in current playlist, if below 4, start downloading.
          change == True means user has asked to change tags.
        """
        mpdq = MPDQueue()
        change = mpdq.watch_playlist(tags=self.tags, user=self.user)
        if change:
            self.user = None
            self.tags = None
            if change == 'to_tag':
                self.ask_for_tag()
            if change == 'to_user':
                self.ask_for_user()
        else:
            if self.tags:
                self.get_albums()
            if self.user:
                self.load_collection()

    def grab_four(self, items):
        """ Return 4 items from list, or all if less than 4 """
        if type(items) is not list:
            items = sorted(items)
        if len(items) > 4:
            return random.sample(items, 4)
        else:
            return random.sample(items, len(items))

    def load_collection(self):
        """ Select tracks, send their urls to get_song_meta """
        tracks = self.grab_four(self.user_collection)
        # item_ids = [t['item_id'] for t in tracks]
        item_urls = [t['item_url'] for t in tracks]
        self.get_song_meta(item_urls)

    def call_album_api(self):
        """ Call API for more songs when playing by tag """
        sort = random.choice(['pop', 'new'])
        hub_data = {"filters": {"format": "all", "location": 0, "sort": sort, "tags": self.tags}, "page": self.page}
        try:
            r = requests.post(self.hub_url, json=hub_data, headers=HEADERS)
            return r.json()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit()

    def get_albums(self):
        """ Get urls of random albums. """
        # Max page number is 30
        if self.page_limit:
            self.page = random.randint(1, int(self.page_limit))
        else:
            self.page = random.randint(1, 3) if not self.page else random.randint(self.page, 30)

        if self.page_limit and self.page_limit < 3:
            msg_few_tag_results(self.tags)

        while True:
            ar = self.call_album_api()
            items = ar.get('items', None)
            self.has_more = ar.get('more-available', None)
            if not items:
                self.page = abs(self.page - 1)
                continue

            if 'items' in ar and len(ar['items']) > 0:
                if self.has_more is False:
                    # Response has items but no more available, so mark page limit
                    self.page_limit = self.page
                break
            else:
                continue

        msg_results_found(self.tags)
        albums = []
        genres = []
        for i in ar['items']:
            albums.append(i['tralbum_url'])
            genres.append(i['genre'])
        all_tags = genres + list(self.related_tags)
        random.shuffle(all_tags)
        at = all_tags[:10]
        if not self.related_tags:
            self.related_tags = genres
        else:
            self.related_tags = set([a for a in at if a]) if at else genres
        msg_related_tags(', '.join(set(self.related_tags)))
        self.get_song_meta(set(albums))

    def get_song_meta(self, albums):
        """
          Choose random song from the passed album
          get metadata (artist, title, album, url, date, dl_url) for that song
        """
        r_albums = self.grab_four(albums)
        band_ids = []
        for a in r_albums:
            try:
                r = requests.get(a, headers=HEADERS)
            except requests.exceptions.RequestException as e:
                print(e)
            if r.status_code != 404:
                soup = BeautifulSoup(r.text, 'lxml')
                # check if song is tagged with anything from banlist
                tags = soup.find_all('a', class_='tag')
                tag_list = [t.text for t in tags]
                at = (list(self.related_tags) + tag_list)[:10]
                self.related_tags = set(at)
                # check track to make sure not tagged with banned genre
                if soup and set(tag_list).isdisjoint(BANNED_GENRES):
                    all_js = soup.find_all('script', type='text/javascript')
                    for j in all_js:
                        tralbum = j.get('data-tralbum')
                        if tralbum:
                            break
                    if not tralbum:
                        continue
                    t_json = json.loads(tralbum)
                    band_id = t_json.get("current").get("band_id")
                    if band_id in band_ids:
                        continue
                    else:
                        band_ids.append(band_id)
                    track_info = t_json["trackinfo"]
                    s = random.choice(track_info)
                    if s.get('file') is not None:
                        isodate = t_json.get('current').get('release_date')
                        date = datetime.datetime.strptime(isodate, '%d %b %Y %H:%M:%S %Z').strftime("%Y-%m-%d") if isodate else ""
                        metadata = {
                            'artist': t_json.get('artist'),
                            'artist_id': f'{band_id}',
                            'title': f'{s.get("title")}',
                            'track': f'{s.get("track_num")}',
                            'track_id': f'{s.get("track_id")}',
                            'album': t_json.get('current').get('title'),
                            'date': date,
                            'album_url': a,
                            'dl_url': s['file'].get('mp3-128'),
                            'genre': ', '.join(set(tag_list)),
                        }
                        ban_check = db.Database.check_ban(metadata['artist_id'], metadata['track_id'])
                        if not ban_check:
                            self.download_song(metadata)
        self.monitor_mpd()

    def download_song(self, metadata):
        dl_url = metadata['dl_url']
        timestamp = int(time())
        fn = ['bctcache', str(timestamp), metadata['artist_id'], metadata['track_id']]
        filename = '_'.join(fn) + '.mp3'
        path = os.path.join(c['cache_dir'], filename)
        # If exists, load, if not dl
        rel_path = c['cache_dir'].split('/')[-1]
        local_path = rel_path + '/' + filename
        if os.path.isfile(path) is True:
            MPDQueue.add_song(local_path)
        else:
            try:
                r = requests.get(dl_url, stream=dl_url, headers=HEADERS)
            except:
                msg_connection_error()
                quit()
            msg_now_loading(metadata['artist'], metadata['title'])
            with open(path, 'wb') as t:
                total_length = int(r.headers.get('content-length', 0))
                for chunk in progress.bar(r.iter_content(
                        chunk_size=1024), expected_size=(total_length / 1024) + 1):
                    if chunk:
                        t.write(chunk)
                        t.flush()
            self.write_ID3_tags(filename, metadata)
            MPDQueue().add_song(local_path)

    def write_ID3_tags(self, filename, metadata):
        path = os.path.join(c['cache_dir'], filename)
        try:
            song = EasyID3(path)
        except ID3NoHeaderError:
            song = File(path, easy=True)
        song['title'] = metadata['title']
        song['tracknumber'] = metadata['track']
        song['artist'] = metadata['artist']
        song['album'] = metadata['album']
        if metadata['genre']:
            song['genre'] = metadata['genre'].title().replace('-', ' ')
        song['date'] = metadata['date']
        song['website'] = metadata['album_url']
        song.save()


def main():
    """
    bandcamp_tagplayer
    Config file at: ~/.config/bandcamp_tagplayer/config

    Options:
      -h --help                 Show this screen.
      -v --version              Show version.

    Code:
        Gregory Parrish
        https://github.com/greggparrish/bandcamp_tagplayer
    """
    import argparse
    p = argparse.ArgumentParser(description='Creates mpd playlists from Bandcamp genre tags.')
    p.add_argument('tags', metavar='tags', type=str, nargs='*', help='Music genre(s)', default=None)
    p.add_argument('-t', '--tags', help='Music genre(s).', action='store', dest='tags2', metavar='tags', default=None, nargs='+')
    p.add_argument('-u', '--user', help='Bandcamp username', action='store', metavar='user', default=None)
    args = p.parse_args()

    try:
        with Tagplayer(tags=(args.tags or args.tags2), user=args.user) as tp:
            tp.check_tag()
    except Exception as e:
        print(f'ERROR: {e}')


if __name__ == '__main__':
    main()
