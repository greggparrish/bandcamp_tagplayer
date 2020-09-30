from blessed import Terminal
from time import sleep


class Messages:
    def creating_db(self):
        print("Creating database")

    def current_song(self, song):
        print(f"Now playing: {song.name} by {song.artist} from {song.album}")

    def menu_choice(self, show):
        term = Terminal()
        print(term.clear())
        print(show)
        sleep(1)
        print(term.clear())

    def few_tag_results(self, tags):
        print(f"Only 1 page of results for: {(', ').join(tags)}.  Maybe try a related genre.")

    def no_tag_results(self, tags):
        print(f"No results tagged: {(', ').join(tags)}")

    def now_loading(self, artist, track):
        print(f"Now loading: {track} by {artist}")

    def results_found(self, tags):
        print(f"Downloading metadata for {(', ').join(tags)} albums")

    def related_tags(self, tags):
        term = Terminal()
        print(term.bold + f"Related tags: {tags}" + term.normal)
