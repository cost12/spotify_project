import song_nodb as song_db
import library

class Tag:
    """
    A way to mark songs as having a certain trait, used to filter for playlists
    """
    def __init__(self):
        pass

class Library(library.Library):
    """
    A collection of songs, basically just a list
    """
    def __init__(self, name, id):
        self.spotify_playlist_id = id
        self.library_name = name
        self.songs = dict[str,song_db.Song]()
        self.artists = dict[str,song_db.Artist]()
        self.albums = dict[str,song_db.Album]()

    def __repr__(self):
        return 'Library: [' + ','.join([song.__repr__() for song in self.songs.values()]) + ']'

    def __contains__(self, song:song_db.Song) -> bool:
        return song.id in self.songs

    def size(self) -> int:
        return len(self.songs)
    
    def length(self) -> int:
        return sum([song.duration_ms for song in self.songs.values()])
    
    def num_artist(self) -> int:
        return len(self.artists)
    
    def num_albums(self) -> int:
        return len(self.albums)

    def add_song(self, song:song_db.Song):
        self.songs[song.id] = song
        for album in song.albums:
            self.albums[album.id] = album
        for artist in song.artists:
            self.artists[artist.id] = artist

    def get_songs(self) -> list[song_db.Song]:
        return list(self.songs.values())
    
    def get_artists(self) -> list[song_db.Song]:
        return list(self.artists.values())
    
    def get_albums(self) -> list[song_db.Song]:
        return list(self.albums.values())
    
    def get(self, type:str) -> list[song_db.Song]|list[song_db.Artist]|list[song_db.Album]:
        if type == 'songs':
            return self.get_songs()
        elif type == 'artists':
            return self.get_artists()
        elif type == 'albums':
            return self.get_albums()

    def name(self) -> str:
        return self.library_name
    
class Playlist(Library):
    """
    A collection of songs, starts from a base library or libraries and applies filters to determine which songs are in
    """
    def __init__(self):
        pass