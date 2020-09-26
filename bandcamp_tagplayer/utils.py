import datetime
import os
import re
import time
import webbrowser

from blessed import Terminal
from mutagen.easyid3 import EasyID3

from .config import Config
from . import db
from .messages import Messages

cf = Config().conf_vars()


class Utils:
    def symlink_musicdir(self):
        """
            Cache has to be within mpd music dir to load tracks,
            so symlink it if user didn't choose a path already in
            their mpd music dir
        """
        try:
            rel_path = cf['cache_dir'].split('/')[-1]
            os.symlink(
                cf['cache_dir'],
                os.path.join(cf['music_dir'], rel_path))
        except FileExistsError:
            pass

    def browser(self, filename):
        """ Open browser with Bandcamp artist url """
        artist_url = EasyID3(
            os.path.join(
                cf['music_dir'],
                filename))['website'][0]
        wb = webbrowser.get(cf['browser']).open(artist_url)
        return wb

    def save_track_info(self, current_song):
        """ Save artist, track, genre & url to text file set in config """
        term = Terminal()
        print(term.normal)
        date = '{0:%b %d, %Y %H:%M:%S}'.format(datetime.datetime.now())
        track = EasyID3(os.path.join(cf['music_dir'], current_song))
        artist = f"Artist: {track['artist'][0]}"
        song = f"Track: {track['title'][0]}"
        genre = f"Genre: {track['genre'][0]}"
        website = track['website'][0]
        with open(cf['save_file'], 'a') as out:
            saved = out.write(f'\n {date} \n {artist} \n {song} \n {genre} \n {website} \n')
        return saved

    def ban(self, item_id, item_type):
        """ Ban either a track or artist, won't dl in future """
        banned = db.Database.ban_item(item_id, item_type)
        return banned

    def clear_cache(self):
        """ Remove Bandcamp mp3s from cache dir if older than a day. Please support the artists. """
        now_ts = int(time.time())
        files = [
            f for f in os.listdir(
                cf['cache_dir']) if os.path.isfile(
                os.path.join(
                    cf['cache_dir'],
                    f))]
        for f in files:
            bc_track = re.findall('bctcache_\d*_\d*_\d*.mp3', f)
            if bc_track:
                ts = int(bc_track[0].split('_')[1])
                if ts + 86400 < now_ts:
                    os.remove(os.path.join(cf['cache_dir'], bc_track[0]))

    def options_menu(self, current_song, change_state):
        """ Render options menu and handle commands """
        change = change_state
        term = Terminal()
        with term.location(0, term.height - 1):
            with term.cbreak():
                c = term.inkey(1)
                if c == 't':
                    change = 'to_tag'
                if c == 'u':
                    print(term.clear())
                    change = 'to_user'
                if c == 'q':
                    print(term.clear())
                    print(term.normal)
                    self.clear_cache()
                    exit()
                if c == 'B':
                    ar_id = current_song.split('_')[3]
                    self.ban(ar_id, 0)
                    show = 'Banning artist'
                    Messages().menu_choice(show)
                if c == 'b':
                    tr_id = current_song.split('_')[4].replace('.mp3', '')
                    self.ban(tr_id, 1)
                    show = 'Banning song'
                    Messages().menu_choice(show)
                if c == 's':
                    show = f"Saving info to {cf['save_file']}"
                    Messages().menu_choice(show)
                    self.save_track_info(current_song)
                if c == 'w':
                    try:
                        EasyID3(os.path.join(cf['music_dir'], current_song))['website'][0]
                        show = 'Opening Bandcamp page'
                        Messages().menu_choice(show)
                        self.browser(current_song)
                    except BaseException:
                        print("No website saved in track meta.")
                        time.sleep(2)
                        print(term.clear())
        return change
