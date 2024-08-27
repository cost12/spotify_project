import rankings
import song_nodb as song_db
import song_collections

class Profile:
    
    def __init__(self, name:str, id:str):
        self.name = name
        self.id = id
        self.libraries = dict[str,song_collections.Library]()
        self.playlists = dict[str,song_collections.Playlist]()
        self.rankings = dict[str,rankings.Ranking]()
        self.spotify_rankings = dict[str,rankings.Ranking]()
        self.tags = list[song_collections.Tag]()

    """
    Ranking stuff
    """

    def has_spotify_ranking(self, term:str) -> bool:
        return term in self.spotify_rankings
    
    def add_spotify_ranking(self, term:str, ranking:list[song_db.Song]) -> None:
        pass

    def get_spotify_ranking(self, term:str) -> list[song_db.Song]:
        pass

    def extend_spotify_ranking(self, term:str, ranking:list[song_db.Song]) -> list[song_db.Song]:
        pass
        
    def init_ranking(self, ranking_type:str, init_type:str, library:str, name:str, desc:str, properties) -> rankings.Ranking:
        lib = self.get_library(library)
        r = rankings.get_ranking(ranking_type,init_type,name,desc,lib,properties)
        self.rankings[r.id] = r
        return r

    def get_headers(self, rank_id='0') -> list[str]:
        return ['Song', 'Artist', 'Album', 'Score']

    def add_rank_result(self, item1:rankings.RankItem, item2:rankings.RankItem, result:float, rank_id:str):
        self.rankings[rank_id].add_result(item1, item2, result)

    def add_item_result(self, rank_id:str, item:rankings.RankItem, amount:float):
        ranking = self.rankings[rank_id]
        if isinstance(ranking, rankings.InexactRanking):
            ranking.adjust_rating(item, amount)

    """
    def get_ranking_items(self, rank_id:str) -> list[dict]:
        items = []
        for i,item in enumerate(self.rankings[rank_id].get_items()):
            items.append({})
            items[i]['id'] = item.id
            items[i]['Song'] = item.name
            items[i]['Artist'] = item.artist_str()
            items[i]['Album'] = item.albums[0].name
            items[i]['Score'] = str(round(self.rankings[rank_id].get_rating(item),3))
        items.sort(key=lambda item:float(item['Score']),reverse=True)
        return items
    """
    def get_ranking_items(self, rank_id:str) -> list:
        return list(self.rankings[rank_id].get_items())
    
    def get_ranking(self, rank_id:str) -> rankings.Ranking:
        return self.rankings[rank_id]
    
    def get_two_items(self, rank_id:str) -> list[rankings.RankItem]:
        ranking = self.rankings[rank_id]
        if isinstance(ranking, rankings.InexactRanking):
            return ranking.get_two()

    def get_ranking_name(self, rank_id:str) -> str:
        return self.rankings[rank_id].get_name()

    def get_ranking_desc(self, rank_id:str) -> str:
        return self.rankings[rank_id].get_description()
    
    def get_rankings(self) -> list[rankings.Ranking]:
        return list(self.rankings.values())
    
    """
    Library stuff
    """

    def get_libraries(self) -> list[song_collections.Library]:
        return list(self.libraries.values())

    def get_num_libraries(self) -> int:
        return len(self.libraries)

    def add_library(self, library:song_collections.Library):
        self.libraries[library.name()] = library

    def get_library(self, lib:str) -> song_collections.Library:
        return self.libraries[lib]

    def get_library_names(self) -> list[str]:
        return list(self.libraries.keys())