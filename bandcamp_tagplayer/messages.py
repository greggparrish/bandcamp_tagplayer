from blessed import Terminal
from time import sleep

CONFIG_FILE = '~/.config/bandcamp_tagplayer/config'


def msg_creating_db():
    print("Creating database")


def msg_current_song(song):
    print(f"Now playing: {song.name} by {song.artist} from {song.album}")


def msg_menu_choice(show):
    term = Terminal()
    print(term.clear())
    print(show)
    sleep(1)
    print(term.clear())


def msg_few_tag_results(tags):
    print(f"Only 1 page of results for: {(', ').join(tags)}.  Maybe try a related genre.")


def msg_no_tag_results(tags):
    print(f"No results tagged: {(', ').join(tags)}")


def msg_now_loading(artist, track):
    print(f"Now loading: {track} by {artist}")


def msg_results_found(tags):
    print(f"Downloading metadata for {(', ').join(tags)} albums")


def msg_related_tags(tags):
    term = Terminal()
    print(term.bold + f"Related tags: {tags}" + term.normal)


def msg_missing_music_dir(music_dir):
    print(f'ERROR: Missing music directory: {music_dir}. Please set mpd music directory in the config file: {CONFIG_FILE}')


def msg_update_error(e):
    print(f'{e}.  If you have a password for mpd, you can set it in {CONFIG_FILE}. If not, make sure field is empty.')


def msg_connection_error():
    print(f'Problem retrieving song.  Please check your internet connection.  Shutting down.\n{e}')
