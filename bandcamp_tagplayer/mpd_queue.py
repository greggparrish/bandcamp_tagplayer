from blessed import Terminal
from time import sleep

from config import Config
from mpd import MPDClient
from utils import Utils

c = Config().conf_vars()


class MPDConn:
    def __init__(self, host, path):
        self.host = c['mpd_host']
        self.port = c['mpd_port']
        self.client = None

    def __enter__(self):
        self.client = MPDClient()
        self.client.connect(c['mpd_host'], c['mpd_port'])
        # 0 is random off, 1 is on
        # self.client.random(0)
        return self.client

    def __exit__(self, exc_class, exc, traceback):
        self.client.close()
        self.client.disconnect()


class MPDQueue(object):
    def add_song(self, song):
        with MPDConn(c['mpd_host'], c['mpd_port']) as m:
            self.update_mpd()
            sleep(5)
            try:
                m.add(song)
            except Exception as exc:
                try:
                    sleep(2)
                    m.add(song)
                except Exception as exc:
                    pass

    def watch_playlist(self, tag=None, user=None):
        '''
        Check playlist every 2 seconds, if under 4 tracks, get more
        '''
        term = Terminal()
        print(term.clear)
        with MPDConn(c['mpd_host'], c['mpd_port']) as m:
            change = None
            curr_song = None
            while True:
                songs_left = len(m.playlist())
                if songs_left <= 3 or change:
                    print(term.clear)
                    break
                else:
                    if m.status()['state'] != 'play':
                        curr_song = 'paused'
                    else:
                        song_check = m.currentsong()['file']
                        if song_check != curr_song:
                            curr_song = song_check
                            print(term.clear)
                    self._write_status(songs_left, tag=tag, user=user)
                    sleep(2)
                change = Utils().options_menu(curr_song, change)
        return change

    def update_mpd(self):
        '''
          Update mpd so it knows of new tracks in bct cache
        '''
        rel_path = c['cache_dir'].split('/')[-1]
        with MPDConn(c['mpd_host'], c['mpd_port']) as m:
            m.update(rel_path)

    def _write_status(self, songs_left, tag=None, user=None):
        '''
          Write current song (if playing), # in playlist, current search tag
          and menu to term
        '''
        with MPDConn(c['mpd_host'], c['mpd_port']) as m:
            cs = m.currentsong()
            if cs != {}:
                genre = cs.get('genre', '')
                title = cs.get('title', '')
                artist = cs.get('artist', '')
            term = Terminal()
            with term.hidden_cursor():
                with term.location(0, 0):
                    if tag:
                        print(f"Search tag: {tag.title()}")
                    if user:
                        print(f"User collection: {user}")
                    print(f"{songs_left} tracks in current playlist")
                    if cs != {}:
                        print(f"\n# Current song \nartist:\t{artist}\ntitle:\t{title}\ntags:\t{genre}")
                    print("\n[c]hange tag, change [u]sername, [p]rofile on BC, [b]an song, [B]an artist, [q]uit")
