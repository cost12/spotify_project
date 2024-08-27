import spotipy
import pickle
from typing import Any

import utils
import song_nodb as song_db
import personal_profile
import song_collections
import rankings
from song_db import SONG_PROPERTIES
import spotify_secrets
#import simple_db

class Control:
    """
    This class serves as a middleman between the html requests and database/ program
    """

    def __init__(self, flask_session):
        self.__spotipy_connect(flask_session)
        self.users = dict[str,personal_profile.Profile]()
        self.song_tracker = song_db.SongTracker()
        self.current_items = []
        self.table_sorts = {'libraries':'name','rankings':'id','ranking':'rating'}
        self.sort_direction = False

    def create_profile(self, user_id:str, user_name:str) -> None:
        if user_id not in self.users:
            self.users[user_id] = personal_profile.Profile(user_name, user_id)

    """
    Interactions with spotify/spotipy
    """

    def validate_session(self) -> tuple[bool,str]:
        if not self.sp_oauth.validate_token(self.cache_handler.get_cached_token()):
            return False, self.sp_oauth.get_authorize_url()
        return True, None
    
    def spotify_access_token(self, code):
        return self.sp_oauth.get_access_token(code)

    def __spotipy_connect(self, flask_session):
        CLIENT_SECRET = spotify_secrets.CLIENT_SECRET
        CLIENT_ID =     spotify_secrets.CLIENT_ID
        REDIRECT_URI = 'http://localhost:5000/callback'
        scope = 'playlist-read-private,user-top-read,user-read-private,user-read-email'
        self.cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(flask_session)

        self.sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id= CLIENT_ID, 
            client_secret= CLIENT_SECRET,
            redirect_uri= REDIRECT_URI,
            scope= scope,
            cache_handler= self.cache_handler,
            show_dialog= True # make false later
        )

        self.sp = spotipy.Spotify(auth_manager=self.sp_oauth)

    def get_playlists(self, user_id) -> list[dict]:
        playlists_info = self.sp.user_playlists(user_id)
        playlists = playlists_info['items']

        while playlists_info['next']:
            playlists_info = self.sp.next(playlists_info)
            playlists.extend(playlists_info['items'])
        return playlists

    def add_playlist_from_spotify(self, user_id:str, playlist_id:str) -> None:
        playlist_name = self.sp.playlist(playlist_id,"name")['name']
        lib = self.playlist_to_library(playlist_id, playlist_name)
        self.users[user_id].add_library(lib)

    def playlist_to_library(self, playlist_id:str, playlist_name:str) -> song_collections.Library:
        library = song_collections.Library(playlist_name,playlist_id)
        items = self.sp.playlist_items(playlist_id,limit=50,offset=0)
        more_info = self.sp.audio_features([item['track']['id'] for item in items['items']])
        while items:
            for item,info in zip(items['items'],more_info):
                #if item['track']['id'] not in self.songs:
                added_at = item['added_at']
                track = item['track']
                track['added_at'] = added_at
                for property in SONG_PROPERTIES:
                    track[property] = info[property]
                library.add_song(self.song_tracker.get_song(track))

            if items['next']:
                items = self.sp.next(items)
                more_info = self.sp.audio_features([item['track']['id'] for item in items['items']])
            else:
                items = None
        return library

    """
    Access ranking information
    """

    def can_create_ranking(self, user_id:str) -> bool:
        return self.users[user_id].get_num_libraries() > 0

    def create_spotify_ranking(self, user_id:str, term:str, library:song_collections.Library):
        if self.users[user_id].has_spotify_ranking(term):
            i = 0
            user_ranking = list[song_db.Song]()
            spotify_ranking = self.user.get_spotify_ranking(term)
            while len(user_ranking) < library.size() and i < len(spotify_ranking):
                song = spotify_ranking[i]
                if song in library:
                    user_ranking.append(song)
                i += 1
            if len(user_ranking) >= library.size():
                return user_ranking
            else:
                return self.__extend_spotify_ranking(user_id, term, library, user_ranking, len(spotify_ranking))
        else:
            return self.__extend_spotify_ranking(user_id, term,library,[])
        
    def __extend_spotify_ranking(self, user_id:str, term:str, library:song_collections.Library, user_ranking:list[song_db.Song], offset:int=0) -> list[song_db.Song]:
        song_info = self.sp.current_user_top_tracks(limit=20,offset=offset,time_range=term)
        more_info = self.sp.audio_features([item['id'] for item in song_info['items']])
        spotify_ranking = list[song_db.Song]()

        while song_info:
            for s_info,m_info in zip(song_info['items'],more_info):
                if s_info['id'] not in self.song_tracker:
                    s_info['added_at'] = 'na'
                    for property in SONG_PROPERTIES:
                        s_info[property] = m_info[property]
                    self.song_tracker.get_song(s_info)

                song = self.song_tracker.song(s_info['id'])
                spotify_ranking.append(song)
                if song in library:
                    user_ranking.append(song)
            if song_info['next'] and len(user_ranking) < library.size():
                song_info = self.sp.next(song_info)
                more_info = self.sp.audio_features([item['id'] for item in song_info['items']])
            else:
                song_info = None
        self.users[user_id].extend_spotify_ranking(term, spotify_ranking)
        return user_ranking

    def initialize_ranking(self, user_id:str, ranking_type:str, seed_type:str, library:str, name:str, desc:str, properties:dict) -> rankings.Ranking:
        if seed_type=='manual':
            r = self.users[user_id].init_ranking(ranking_type, 'properties', library, name,desc, properties)
            return r
        elif seed_type in ['spotify-long-term','spotify-medium-term','spotify-short-term']:
            term = utils.subsrting_from_to(seed_type,'-','-')
            order = self.create_spotify_ranking(user_id, f"{term}_term",self.users[user_id].get_library(library))
            r = self.users[user_id].init_ranking(ranking_type,'order',library,name,desc,order)
            return r
        else:
            print(seed_type)
            raise NotImplemented
        
    def get_two_items(self, user_id:str, ranking_id:str) -> list[rankings.RankItem]:
        return self.users[user_id].get_two_items(ranking_id)
    
    def get_expected_outcome(self, user_id:str, ranking_id:str, item1_id:str, item2_id:str) -> float:
        return self.users[user_id].get_ranking(ranking_id).expected_outcome(self.id_to_item(item1_id),self.id_to_item(item2_id))

    def get_item_info(self, user_id:str, ranking_id:str, item:rankings.RankItem) -> dict[str,str]:
        item_info = {
            "name":   item.name,
            'id':     item.id,
            'link':   item.link,
            'image': item.get_album().get_image(),
            'preview':item.preview_url,
            "artist": item.artist_str(),
            "rank":   self.get_item_rank(user_id, ranking_id, item),
            "rating": self.get_item_rating(user_id, ranking_id, item),
            "k value": self.get_item_kvalue(user_id, ranking_id, item),
            "comparisons": self.get_item_comparisons(user_id, ranking_id, item)
        }
        return item_info
    
    def get_ranking_items(self, user_id:str, ranking_id:str) -> list[dict]:
        return self.users[user_id].get_ranking_items(ranking_id)
    
    def get_item_rank(self, user_id:str, ranking_id:str, item:rankings.RankItem):
        ranking = self.users[user_id].get_ranking(ranking_id)
        return ranking.get_rank(item)
    
    def get_item_rating(self, user_id:str, ranking_id:str, item:rankings.RankItem):
        ranking = self.users[user_id].get_ranking(ranking_id)
        return ranking.get_rating(item)
    
    def get_item_kvalue(self, user_id:str, ranking_id:str, item:rankings.RankItem):
        ranking = self.users[user_id].get_ranking(ranking_id)
        return ranking.get_kvalue(item)
    
    def get_item_comparisons(self, user_id:str, ranking_id:str, item:rankings.RankItem):
        ranking = self.users[user_id].get_ranking(ranking_id)
        return ranking.get_comparisons(item)

    def get_rankings_info(self, user_id:str) -> list[rankings.Ranking]:
        rankings = self.users[user_id].get_rankings()
        info = [self.get_ranking_info(ranking) for ranking in rankings]
        info.sort(key=lambda rank: rank[self.table_sorts['rankings']], reverse=self.sort_direction)
        return info
    
    def get_ranking_info(self, ranking:rankings.Ranking) -> dict[str,Any]:
        rank_dict = {}
        rank_dict['id'] = ranking.id
        rank_dict['name'] = ranking.get_name()
        rank_dict['library'] = ranking.library_name()
        rank_dict['num_songs'] = ranking.size()
        rank_dict['num_comparisons'] = ranking.num_comparisons()
        rank_dict['description'] = ranking.get_description()
        return rank_dict
    
    def get_ranking_name(self, user_id:str, ranking_id:str) -> str:
        return self.users[user_id].get_ranking_name(ranking_id)
    
    def get_ranking_desc(self, user_id:str, ranking_id:str) -> str:
        return self.users[user_id].get_ranking_desc(ranking_id)
    
    def add_rank_result(self, user_id:str, ranking_id:str, item1_id:str, item2_id:str, result:float) -> None:
        item1 = self.id_to_item(item1_id)
        item2 = self.id_to_item(item2_id)
        self.users[user_id].add_rank_result(item1, item2, result, ranking_id)

    def add_item_result(self, user_id:str, ranking_id:str, item_id:str, result:float) -> None:
        self.users[user_id].add_item_result(ranking_id, self.id_to_item(item_id), result)

    """
    Access libraries
    """
    def get_library_names(self, user_id:str) -> list[str]:
        return self.users[user_id].get_library_names()
    
    def get_libraries_info(self, user_id:str) -> list[dict[str,Any]]:
        libraries = self.users[user_id].get_libraries()
        info = [self.get_library_info(library) for library in libraries]
        info.sort(key=lambda lib: lib[self.table_sorts['libraries']], reverse=self.sort_direction)
        return info

    def get_library_info(self, library:song_collections.Library) -> dict[str,Any]:
        lib_dict = {}
        lib_dict['name'] = library.name()
        lib_dict['songs'] = library.size()
        lib_dict['albums'] = library.num_albums()
        lib_dict['artists'] = library.num_artist()
        lib_dict['average'] = utils.ms_to_str(library.length()//library.size())
        return lib_dict
    
    """
    Tables!
    """
    def set_table_sort(self, table:str, sort:str) -> None:
        if sort == self.table_sorts[table]:
            self.sort_direction = not self.sort_direction
        else:
            self.table_sorts[table] = sort

    def get_table_sort(self, table:str) -> str:
        return self.table_sorts[table]

    """
    Access/ use the database
    """
    def id_to_item(self, item:str) -> rankings.RankItem:
        return self.song_tracker.song(item)

    def load_to_db(self, user_id:str):
        pass

    def load_from_db(self, user_id:str):
        pass

    """
    Access/ use files
    """
    def load_to_file(self, user_id:str):
        with open(f'static/data/pickle/{user_id}.pckl','wb') as f:
            pickle.dump((self.users[user_id],rankings.Ranking.id_num),f)
        with open(f'static/data/pickle/song_tracker.pckl', 'wb') as f:
            pickle.dump(self.song_tracker,f)

    def load_from_file(self, user_id:str):
        with open(f'static/data/pickle/{user_id}.pckl','rb') as f:
            self.users[user_id],rankings.Ranking.id_num = pickle.load(f)
        with open(f'static/data/pickle/song_tracker.pckl', 'rb') as f:
            self.song_tracker = pickle.load(f)