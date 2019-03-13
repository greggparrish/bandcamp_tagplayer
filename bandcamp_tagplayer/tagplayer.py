import datetime
import json
import os
import random
import re
import sys
from time import sleep, time

from blessed import Terminal
from bs4 import BeautifulSoup
from clint.textui import progress
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3
import requests

from config import Config
import db
from mpd_queue import MPDQueue
from messages import Messages
from utils import Utils

c = Config().conf_vars()
BANNED_GENRES = [g.lower().strip() for g in c['banned_genres'].split(',')]
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}


class Tagplayer:

    def __init__(self, tag=None, user=None):
        self.metadata = {}
        self.numpages = False
        self.tag = tag
        self.user = user
        self.user_collection = []

    def __enter__(self):
        """ Symlink mpd dir, clear out old downloads, update MPD """
        ut = Utils()
        ut.symlink_musicdir()
        ut.clear_cache()
        db.Database()
        MPDQueue().update_mpd()
        return self

    def __exit__(self, exc_class, exc, traceback):
        if exc:
            return False
        else:
            return True

    def ask_for_tag(self):
        """
          If started without tag or user changed tag through menu, get and slugify tag
        """
        while True:
            term = Terminal()
            print(term.clear())
            tag = input("Enter a tag: ")
            if tag:
                self.tag = re.sub(' ', '-', tag)
                break
            else:
                continue
        self.check_tag()

    def ask_for_user(self):
        """
          Get a username to stream their collection
        """
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
        username = re.split('/', self.user)[-1] if '/' in self.user else self.user
        user_url = f'https://bandcamp.com/{username}'
        user_page = requests.get(user_url, headers=HEADERS)
        if user_page.status_code != requests.codes.ok:
            print(f'User {self.username} does not appear to be a valid user.')
            sys.exit()
        soup = BeautifulSoup(user_page.content, 'lxml')
        pagedata = soup.find('div', id='pagedata')
        if not pagedata:
            print(f'User page for {username} missing data.')
            sys.exit()
        pj = json.loads(pagedata.get('data-blob'))
        collection_count = pj.get('current_fan', 0).get('collection_count', 0)
        fan_id = pj.get('fan_data').get('fan_id')
        last_token = pj.get('collection_data').get('last_token')
        self.parse_tracks(pj, page=True)
        cc = 0 if collection_count <= 45 else collection_count
        print(f'Found {cc} tracks for {username}')
        while cc > 0:
            print(f'Gathering data: {cc} tracks left')
            post_data = {'fan_id': fan_id, 'older_than_token': last_token, 'count': 40}
            user_api_url = 'https://bandcamp.com/api/fancollection/1/collection_items'
            r = requests.post(user_api_url, json=post_data, headers=HEADERS)
            np = r.json()
            self.parse_tracks(np, api=True)
            cc -= 40
        self.load_collection()

    def parse_tracks(self, tracks, page=None, api=None):
        """ Get track data from API response, load into self.user_collection """
        if page:
            tl = tracks.get('item_cache').get('collection')
            new_tracks = [{'item_id': tl[t]['item_id'], 'item_url': tl[t]['item_url'], 'tralbum_type': tl[t]['tralbum_type']} for t in tl]
        else:
            tl = tracks.get('items')
            new_tracks = [{'item_id': t['item_id'], 'item_url': t['item_url'], 'tralbum_type': t['tralbum_type']} for t in tl]
        self.user_collection += new_tracks
        return True

    def check_tag(self):
        """
          Verify that a tag has albums, and get the number of pages of the results.
          More obscure genres might only have a few albums, so we need the number of
          pages to randomize within page limits.
        """
        if self.user:
            self.get_user_collection()
            return
        elif not self.tag and not self.user:
            self.ask_for_tag()
        elif self.tag.lower() in BANNED_GENRES:
            print(f'\nTag {self.tag} is banned in your config file.\nEither remove it from your ban_list or choose another tag.')
            sleep(2)
            self.ask_for_tag()
        else:
            try:
                r = requests.get(f'https://bandcamp.com/tag/{self.tag}?sort_field=new&page=1', headers=HEADERS)
            except Exception as e:
                print(e)
            soup = BeautifulSoup(r.text, 'lxml')
            album_list = soup.find_all('li', class_='item')
            if self.numpages is False:
                pages = soup.find_all('a', class_='pagenum')
                if not pages and album_list != '':
                    self.numpages = 1
                else:
                    self.numpages = pages[-1].contents[0]
            if not album_list:
                Messages().no_tag_results(self.tag)
                sleep(1)
                self.ask_for_tag()
            if self.numpages is not False:
                self.monitor_mpd()

    def monitor_mpd(self):
        """
          Keep watch of the  number of songs in current playlist,
          if below 4, start downloading.
          change == True means user has asked to change tag.
        """
        mpdq = MPDQueue()
        change = mpdq.watch_playlist(tag=self.tag, user=self.user)
        if change:
            self.user = None
            self.tag = None
            if change == 'to_tag':
                self.ask_for_tag()
            if change == 'to_user':
                self.ask_for_user()
        else:
            if self.tag:
                self.get_albums()
            if self.user:
                self.load_collection()

    def grab_four(self, items):
        """
            Return 4 items from list, or all if less than 4
        """
        if len(items) > 4:
            return random.sample(items, 4)
        else:
            return random.sample(items, len(items))

    def load_collection(self):
        tracks = self.grab_four(self.user_collection)
        # item_ids = [t['item_id'] for t in tracks]
        item_urls = [t['item_url'] for t in tracks]
        self.get_song_meta(item_urls)

    def get_albums(self):
        """ Get urls of random albums. """
        sort = random.choice(['pop', 'new'])
        if self.numpages != 1:
            page = random.randint(1, int(self.numpages))
        else:
            page = 1
            Messages().few_tag_results(self.tag)
        try:
            r = requests.get(f'https://bandcamp.com/tag/{self.tag}?from=related&page={page}&sort_field={sort}', headers=HEADERS)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit()
        if r.status_code != 404:
            Messages().results_found(self.tag)
            soup = BeautifulSoup(r.text, 'lxml')
            album_list = soup.find_all('li', class_='item')
            tags = soup.find_all('a', class_='related_tag')
            tag_list = ', '.join([t.text for t in tags])
            Messages().related_tags(tag_list)
            albums = []
            for a in album_list:
                if a:
                    albums.append(a.find('a')['href'])
        self.get_song_meta(albums)

    def get_song_meta(self, albums):
        """
          Choose random song from the passed album
          get metadata (artist, title, album, url, date, dl_url) for that song
        """
        r_albums = self.grab_four(albums)
        for a in r_albums:
            try:
                r = requests.get(a, headers=HEADERS)
            except requests.exceptions.RequestException as e:
                print(e)
            if r.status_code != 404:
                soup = BeautifulSoup(r.text, 'lxml')
                # check if song is tagged with anything from banlist
                tags = soup.find_all('a', class_='tag')
                tag_list = []
                for t in tags:
                    tag_list.append(str(t.text.split('/')))
                # check track to make sure not tagged with banned genre
                if soup and set(tag_list).isdisjoint(BANNED_GENRES):
                    """ album meta from bs4 & current: """
                    artist = soup.find('span', itemprop='byArtist')
                    if artist:
                        artist = artist.find('a').text
                        bc_meta = re.search('current\: (.*?)},', r.text).group(1)
                        m_json = json.loads(bc_meta + '}')
                        if 'release_date' in m_json:
                            full_date = m_json['release_date']
                        elif 'publish_date' in m_json:
                            full_date = m_json['publish_date']
                        full_date = full_date if full_date else str(datetime.datetime.now().year)
                        dm = re.search('\d{4}', full_date)
                        date = dm.group(0)
                        """ song meta from trackinfo: """
                        songs = re.search('trackinfo\: \[(.*)\]', r.text).group(1)
                        s_json = json.loads(f'[{songs}]')
                        s = random.choice(s_json)
                        if s['file'] is not None:
                            metadata = {
                                'artist': artist,
                                'artist_id': str(m_json['band_id']),
                                'track': s['title'],
                                'track_id': str(s['track_id']),
                                'album': m_json['title'],
                                'date': date,
                                'album_url': a,
                                'dl_url': s['file']['mp3-128'],
                                'genre': self.tag,
                            }
                            ban_check = db.Database.check_ban(metadata['artist_id'], metadata['track_id'])
                            if not ban_check:
                                self.download_song(metadata)
        self.monitor_mpd()

    def download_song(self, metadata):
        dl_url = metadata['dl_url']
        timestamp = int(time())
        fn = [
            'bctcache',
            str(timestamp),
            metadata['artist_id'],
            metadata['track_id']]
        filename = '_'.join(fn) + '.mp3'
        path = os.path.join(c['cache_dir'], filename)
        """ If exists, load, if not dl """
        rel_path = c['cache_dir'].split('/')[-1]
        local_path = rel_path + '/' + filename
        if os.path.isfile(path) is True:
            MPDQueue.add_song(local_path)
        else:
            try:
                r = requests.get(dl_url, stream=dl_url, headers=HEADERS)
            except requests.exceptions.RequestException as e:
                print(e)
                quit()
            Messages().now_loading(metadata['artist'], metadata['track'])
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
        song['title'] = metadata['track']
        song['artist'] = metadata['artist']
        song['album'] = metadata['album']
        if metadata['genre']:
            song['genre'] = metadata['genre'].title().replace('-', ' ')
        song['date'] = metadata['date']
        song['website'] = metadata['album_url']
        song.save()


if __name__ == '__main__':
    tag = False
    try:
        with Tagplayer(tag) as tp:
            tp.ask_for_tag()
    except Exception as e:
        print(f'ERROR: {e}')
