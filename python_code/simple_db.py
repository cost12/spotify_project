from flask_sqlalchemy import SQLAlchemy
from db import db
from spotipy import Spotify

from song_db import SONG_PROPERTIES

class Song(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    duration = db.Column(db.Integer)
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

class Artist(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    link = db.Column(db.String)
    followers = db.Column(db.Integer)
    name = db.Column(db.String)
    popularity = db.Column(db.Integer)

class Album(db.Model):
    id = db.Column(db.String, nullable=False, primary_key=True)
    album_type = db.Column(db.String)
    total_tracks = db.Column(db.Integer)
    link = db.Column(db.String)
    name = db.Column(db.String)
    release_date = db.Column(db.String)
    release_date_precision = db.Column(db.String)
    label = db.Column(db.String)
    popularity = db.Column(db.Integer)

class Ranking(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String)
    desc = db.Column(db.String)
    total_mult = db.Column(db.Double)
    elo_mult = db.Column(db.Double)
    total_add = db.Column(db.Double)

    duration = db.Column(db.Integer)
    acousticness = db.Column(db.Double)
    danceability = db.Column(db.Double)
    energy = db.Column(db.Double)
    instrumentalness = db.Column(db.Double)
    liveness = db.Column(db.Double)
    loudness = db.Column(db.Double)
    speechiness = db.Column(db.Double)
    tempo = db.Column(db.Double)
    valence = db.Column(db.Double)

class SongRank(db.Model):
    rank_id = db.Column(db.Integer, nullable=False, primary_key=True)
    song_id = db.Column(db.String, nullable=False, primary_key=True)
    comparisons = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Double, nullable=False)

class SongArtist(db.Model):
    song_id = db.Column(db.String, nullable=False, primary_key=True)
    artist_id = db.Column(db.String, nullable=False, primary_key=True)

class SongAlbum(db.Model):
    song_id = db.Column(db.String, nullable=False, primary_key=True)
    album_id = db.Column(db.String, nullable=False, primary_key=True)

class AlbumArtist(db.Model):
    album_id = db.Column(db.String, nullable=False, primary_key=True)
    artist_id = db.Column(db.String, nullable=False, primary_key=True)

class Library(db.Model):
    library_name = db.Column(db.String, nullable=False, primary_key=True)
    song_id = db.Column(db.String, nullable=False, primary_key=True)