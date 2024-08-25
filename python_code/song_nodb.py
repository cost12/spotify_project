from rankings import RankItem

SONG_PROPERTIES = ['acousticness','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','valence','duration_ms']

"""
TODO: 
 - move 2 songs from rank to control
 - move current rank from profile to control
 - rank should be stored as a dict so rankings can be deleted
 - active ranking html should be active_ranking/id where id is the id of the current ranking
 - ^ same for ranking_results/id

In the Future:
 - ranking Artists/ Albums
 - select Library/ Playlist to rank from
 - load multiple library/ playlist from spotify
 - long term storage of data/ database
 - 30 second preview of songs to rankings
 - click on songs in rankings to see a page about the song/ more details
 - ^ same for artists and albums
 - use ItemLabels to control ratings
 - ability to change range of current rankings
 - exact rankings/sort

 To fix:
  - elo schedule
"""

class Song(RankItem):
    def __init__(self,id,albums,duration_ms,is_playable,name,popularity,preview_url,track_number,link,added_at,acousticness,
                 danceability,energy,instrumentalness,liveness,loudness,speechiness,tempo,valence,artists):
        self.id = id
        self.albums = albums
        self.duration_ms = duration_ms
        self.is_playable = is_playable
        self.name = name
        self.popularity = popularity
        self.preview_url = preview_url
        self.track_number = track_number
        self.link = link
        self.added_at = added_at
        self.acousticness = acousticness
        self.danceability = danceability
        self.energy = energy
        self.instrumentalness = instrumentalness
        self.liveness = liveness
        self.loudness = loudness
        self.speechiness = speechiness
        self.tempo = tempo
        self.valence = valence
        self.rankings = []
        self.artists = artists

    def __repr__(self):
        return f'Song: {self.name} at {hex(id(self))}'
    
    def __eq__(self, other:object) -> bool:
        return isinstance(other,Song) and other.id == self.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def get_album(self):
        return self.albums[0]

    def artist_str(self):
        return ", ".join([artist.name for artist in self.artists])

class Artist(RankItem):
    def __init__(self,id,link,name,popularity=0,followers=0):
        self.id = id
        self.link = link
        self.followers = followers
        self.name = name
        self.popularity = popularity
        self.albums = []
        self.songs = []
        self.genres = []

    def add_song(self,song):
        self.songs.append(song)

    def add_album(self,album):
        self.albums.append(album)

class Album(RankItem):
    def __init__(self,id,album_type,total_tracks,link,name,release_date,release_date_precision,image):
        self.id = id
        self.album_type = album_type
        self.total_tracks = total_tracks
        self.link = link
        self.name = name
        self.release_date = release_date
        self.release_date_precision = release_date_precision
        self.image = image
        self.label = ""
        self.popularity = 0
        self.songs = []
        self.artists = []

    def get_image(self):
        return self.image

    def add_song(self, song):
        self.songs.append(song)
    
class SongTracker:
    """
    This class is in charge of creating an instance of each song, album, and artist and ensuring
    that only one copy of each song/album/artist is created
    """

    def __init__(self):
        self.songs = dict[str,Song]()
        self.artists = dict[str,Artist]()
        self.albums = dict[str,Album]()

    def __contains__(self, song:str):
        return song in self.songs

    def song(self, id:str) -> Song:
        return self.songs[id]
    
    def artist(self, id:str) -> Artist:
        return self.artists[id]
    
    def album(self, id:str) -> Album:
        return self.albums[id]

    def get_song(self, songinfo:dict) -> Song:
        if songinfo['id'] not in self.songs:
            album = self.get_album(songinfo['album'])
            artists=list[Artist]()
            for artist in songinfo['artists']:
                artist_obj = self.get_artist(artist)
                artist_obj.add_album(album)
                artists.append(artist_obj)
            if songinfo['id'] not in self.songs:
                props = {}
                for property in SONG_PROPERTIES:
                    props[property] = songinfo[property]

                s = Song(id=songinfo['id'], duration_ms=songinfo['duration_ms'], albums=[album], artists=artists,
                        is_playable=songinfo.get('is_playable',False), name=songinfo['name'], popularity=songinfo['popularity'],
                        preview_url=songinfo['preview_url'], track_number=songinfo['track_number'], 
                        link=songinfo['external_urls']['spotify'], added_at=songinfo['added_at'],
                        acousticness=songinfo['acousticness'],
                        danceability=songinfo['danceability'],
                        energy=songinfo['energy'],
                        instrumentalness=songinfo['instrumentalness'],
                        liveness=songinfo['liveness'],
                        loudness=songinfo['loudness'],
                        speechiness=songinfo['speechiness'],
                        tempo=songinfo['tempo'],
                        valence=songinfo['valence'])

                album.add_song(s)
                for artist in artists:
                    artist.add_song(s)

                self.songs[s.id] = s
        return self.songs[songinfo['id']]
        
    def get_album(self, albuminfo:dict) -> Album:
        if albuminfo['id'] not in self.albums:
            # TODO: get popularity and label
            if len(albuminfo['images']) > 0:
                image = albuminfo['images'][0]['url']
            else:
                image = '../static/images/badlands.jpg'
            a = Album(id=albuminfo['id'], album_type=albuminfo['album_type'], total_tracks=albuminfo['total_tracks'],
                    link=albuminfo['external_urls']['spotify'], name=albuminfo['name'], release_date=albuminfo['release_date'],
                    release_date_precision=albuminfo['release_date_precision'],image=image)#, label=album['label'],
                    #popularity=album['popularity'])
            
            for artist in albuminfo['artists']:
                a.artists.append(artist)

            self.albums[a.id] = a
        return self.albums[albuminfo['id']]

    def get_artist(self, artistinfo:dict) -> Artist:
        if artistinfo['id'] not in self.artists:
            a = Artist(id=artistinfo['id'], link=artistinfo['external_urls']['spotify'],name=artistinfo['name'])#, #followers=artist['followers']['total'],
            #popularity=artist['popularity'])

            #for genre in artist['genres']:
            #    a.genres.append(genre)

            self.artists[a.id] = a

        return self.artists[artistinfo['id']]