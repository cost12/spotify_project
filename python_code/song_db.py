from flask_sqlalchemy import SQLAlchemy
from db import db
from spotipy import Spotify

SONG_PROPERTIES = ['acousticness','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','valence','duration_ms']

"""
AlbumArtist = db.Table('album_artist',
    db.Column('artist_id', db.String, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('album_id', db.String, db.ForeignKey('album.id'), primary_key=True)
)

SongArtist = db.Table('song_artist',
    db.Column('song_id', db.String, db.ForeignKey('song.id'), primary_key=True),
    db.Column('artist_id', db.String, db.ForeignKey('artist.id'), primary_key=True)
)

ArtistGenre = db.Table('artist_genre',
    db.Column('artist_id', db.String, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('genre', db.String, primary_key=True)
)
"""
class SongRank(db.Model):
    ranking_id = db.Column(db.Integer, db.ForeignKey('ranking.id'), primary_key=True)
    song_id = db.Column(db.String, db.ForeignKey('song.id'), primary_key=True)
    score = db.Column(db.Double)

    ranking = db.relationship('Ranking', back_populates='songs')
    song = db.relationship('Song', back_populates='rankings')

class Ranking(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String)
    desc = db.Column(db.String)
    songs = db.relationship('SongRank', back_populates='ranking')

class Song(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    #album_id = db.Column(db.String, db.ForeignKey('album.id'))
    duration_ms = db.Column(db.Integer)
    is_playable = db.Column(db.Boolean)
    name = db.Column(db.String, nullable=False)
    popularity = db.Column(db.Integer)
    preview_url = db.Column(db.String)
    track_number = db.Column(db.Integer)
    link = db.Column(db.String)
    added_at = db.Column(db.String)
    acousticness = db.Column(db.Double)
    danceability = db.Column(db.Double)
    energy = db.Column(db.Double)
    instrumentalness = db.Column(db.Double)
    liveness = db.Column(db.Double)
    loudness = db.Column(db.Double)
    speechiness = db.Column(db.Double)
    tempo = db.Column(db.Double)
    valence = db.Column(db.Double)
    rankings = db.relationship('SongRank', back_populates='song')
    #artists = db.relationship('artist', secondary=SongArtist, backref='song')

"""
class Artist(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    link = db.Column(db.String)
    followers = db.Column(db.Integer)
    name = db.Column(db.String)
    popularity = db.Column(db.Integer)
    albums = db.relationship('album', secondary=AlbumArtist, backref='artist')
    songs = db.relationship('song', secondary=SongArtist, backref='artist')
    genres = db.relationship('', secondary=ArtistGenre, backref='artist')

class Album(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    album_type = db.Column(db.String)
    total_tracks = db.Column(db.Integer)
    link = db.Column(db.String)
    name = db.Column(db.String)
    release_date = db.Column(db.String)
    release_date_precision = db.Column(db.String)
    #label = db.Column(db.String)
    #popularity = db.Column(db.Integer)
    songs = db.relationship('song', backref='album')
    artists = db.relationship('artist', secondary=AlbumArtist, backref='album')
"""

def get_num_songs():
    return db.session.query(Song).count()

def add_playlist_to_db(playlist_id:str, sp:Spotify):
    items = sp.playlist_items(playlist_id,limit=50,offset=0)
    more_info = sp.audio_features([item['track']['id'] for item in items['items']])
    while items:
        for item,info in zip(items['items'],more_info):
            added_at = item['added_at']
            track = item['track']
            track['added_at'] = added_at
            for property in SONG_PROPERTIES:
                track[property] = info[property]
            add_song(track)

        if items['next']:
            items = sp.next(items)
            more_info = sp.audio_features([item['track']['id'] for item in items['items']])
        else:
            items = None

def add_liked_songs_to_db(sp:Spotify):
    pass

def add_song(song:dict):
    #add_album(song['album'])
    #for artist in song['artists']:
    #    add_artist(artist)

    props = {}
    for property in SONG_PROPERTIES:
        props[property] = song[property]

    s = Song(id=song['id'], duration_ms=song['duration_ms'], #album_id=song['album']['id'],
             is_playable=song.get('is_playable',False), name=song['name'], popularity=song['popularity'],
             preview_url=song['preview_url'], track_number=song['track_number'], 
             link=song['external_urls']['spotify'], added_at=song['added_at'],
             acousticness=song['acousticness'],
             danceability=song['danceability'],
             energy=song['energy'],
             instrumentalness=song['instrumentalness'],
             liveness=song['liveness'],
             loudness=song['loudness'],
             speechiness=song['speechiness'],
             tempo=song['tempo'],
             valence=song['valence'])

    db.session.add(s)
    db.session.commit()

#acousticness,danceability,energy,instrumentalness,liveness,loudness,speechiness,tempo,valence,duration_ms
def init_ranking(name:str, desc:str, acousticness,danceability,energy,instrumentalness,liveness,loudness,speechiness,tempo,valence,duration_ms):
    r = Ranking(name=name, desc=desc)
    result = db.session.query(Song).all()
    ranks = []
    for row in result:
        score = row.acousticness*acousticness+ \
                row.danceability*danceability+ \
                row.energy*energy+ \
                row.instrumentalness*instrumentalness+ \
                row.liveness*liveness+ \
                row.loudness*loudness+ \
                row.speechiness*speechiness+ \
                row.tempo*tempo+ \
                row.valence*valence+ \
                row.duration_ms*duration_ms
        
        sr = SongRank(ranking_id = r.id, song_id = row.id, score=score)
        sr.ranking = r
        row.rankings.append(r)
        ranks.append(sr)

    db.session.add(r)
    db.session.add(ranks)
    db.session.commit()

"""
def add_album(album:dict):
    a = Album(id=album['id'], album_type=album['album_type'], total_tracks=album['total_tracks'],
              link=album['external_urls']['spotify'], name=album['name'], release_date=album['release_date'],
              release_date_precision=album['release_date_precision'])#, label=album['label'],
              #popularity=album['popularity'])
    
    for artist in album['artists']:
        a.artists.append(artist)

    db.session.add(a)
    db.session.commit()

def add_artist(artist:dict):
    a = Artist(id=artist['id'], link=artist['external_urls']['spotify'], followers=artist['followers']['total'],
               popularity=artist['popularity'])

    for genre in artist['genres']:
        a.genres.append(genre)

    db.session.add(a)
    db.session.commit()
"""