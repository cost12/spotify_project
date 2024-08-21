import random
import datetime

from library import Library
import utils

class RankAnalyzer:
    """
    Analyze information gathered from rankings
    This includes:
        artist information
        album information
        how many comparisons have been made/ how sorted it is
        how similar/ different 2 rankings might be
    """
    def __init__(self):
        pass

class RankItem:
    def __init__(self):
        pass

class ItemLabel(RankItem):
    """
    These are items that can be placed into lists to give a description of value
    For example, you might include Bad, Good, Great labels in a ranking to determine
    where the cutoffs are between each of these labels
    """
    def __init__(self, name:str, description:str, *, value=None):
        self.name = name
        self.description = description
        self.value = value # if the label should have a numeric value assiciated with it

    def get_value(self) -> float|None:
        return self.value
    
class Comparison:
    def __init__(self,item1:RankItem,item2:RankItem,result:float):
        self.item1 = item1
        self.item2 = item2
        self.result = result
        self.time = datetime.datetime.now()

class Ranking:
    id_num=0
    def __init__(self):
        pass

    def rating_type(self) -> str:
        pass

    def sync_library(self) -> None:
        pass

    def get_rank(self, item:RankItem) -> int:
        pass

    def get_order(self) -> list[RankItem]:
        pass

    def unranked_items(self) -> list[RankItem]:
        pass

    def get_items(self) -> list[RankItem]:
        pass

    def add_result(self, item1:RankItem, item2:RankItem, result1:float) -> None:
        pass

    def get_name(self) -> str:
        pass

    def get_description(self) -> str:
        pass

    def size(self) -> int:
        pass

    def num_comparisons(self) -> int:
        pass

    def library_name(self) -> str:
        pass

class ExactRanking(Ranking):
    def __init__(self, name:str, desc:str, library:Library, item_ratings:dict[RankItem,float],*,item_type='songs'):
        """
        item_ratings is only the sorted songs
        """
        self.id = str(Ranking.id_num)
        Ranking.id_num += 1
        
        self.name = name
        self.description = desc
        self.item_type = item_type

    def resort(self) -> None:
        pass

    def rating_type(self) -> str:
        return 'exact'

class InexactRanking(Ranking):
    def __init__(self, name:str, desc:str, library:Library, item_ratings:dict[RankItem,float], attribute_vals:dict[str,float],*,min_elo:float=1400,max_elo=1600,item_type='songs'):
        self.id = str(Ranking.id_num)
        Ranking.id_num += 1

        self.name = name
        self.description = desc
        self.item_type = item_type

        utils.adjust_range(item_ratings, min_elo, max_elo, change_vals=True)
        self.item_ratings = utils.EloSystem(item_ratings)
        self.total_mult = 1
        self.total_add = 0

        self.comparisons = list[Comparison]()
        self.library = library
        self.attribute_vals = attribute_vals
        self.adjust_range(0,100)

    def library_name(self) -> str:
        return self.library.name()

    def size(self) -> int:
        return self.library.size()
    
    def num_comparisons(self) -> int:
        return len(self.comparisons)

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def rating_type(self) -> str:
        return "inexact"
    
    def unranked_items(self) -> list[RankItem]:
        return filter(lambda x: x not in self.item_ratings.get_items(), self.library.get(self.item_type))

    def adjust_range(self, min_val:float=0, max_val:float=100) -> None:
        mult,add = utils.adjust_range(self.item_ratings.ratings,min_val,max_val)
        self.total_mult *= mult
        self.total_add += add

    def expected_outcome(self, item1:RankItem, item2:RankItem) -> float:
        return self.item_ratings.expected_outcome(item1,item2)
    
    def get_kvalue(self, item:RankItem) -> float:
        return self.total_mult*self.item_ratings.get_kvalue(item)

    def get_init_rating(self, item:RankItem) -> float:
        return get_attribute_rating(item,self.attribute_vals)

    def get_two(self) -> list[RankItem]:
        return random.sample(list(self.item_ratings.get_items()),k=2)

    def add_result(self, item1:RankItem, item2:RankItem, result1:float) -> None:
        self.comparisons.append(Comparison(item1,item2,result1))
        self.item_ratings.add_result(item1,item2,result1)

    def adjust_rating(self, item:RankItem, amount:float) -> None:
        self.comparisons.append(Comparison(item,None,amount))
        self.item_ratings.adjust_rating(item,amount)

    def get_kvalue(self, item:RankItem) -> int:
        return self.total_mult*self.item_ratings.get_kvalue(item)
    
    def get_comparisons(self, item:RankItem) -> int:
        return self.item_ratings.get_comparisons(item)

    def get_rank(self, item:RankItem) -> int:
        return self.item_ratings.get_rank(item)

    def get_rating(self, item:RankItem) -> float:
        return self.total_mult*self.item_ratings.get_rating(item)+self.total_add
    
    def get_order(self) -> list[RankItem]:
        return self.item_ratings.get_order()
    
    def get_items(self) -> list[RankItem]:
        return self.item_ratings.get_items()
    
def get_attribute_rating(item:RankItem, attribute_vals:dict[str,float]):
    rat = 0
    for attr in attribute_vals:
        rat += getattr(item, attr)*attribute_vals[attr]
    return rat

def get_ranking(ranking_type:str, init_type:str, name:str, desc:str, library:Library, info,*,rank_item='songs') -> Ranking:
    if ranking_type == 'exact':
        pass
    elif ranking_type == 'inexact':
        if init_type == 'order':
            item_ratings = dict[RankItem,float]()
            for i,item in enumerate(info):
                item_ratings[item] = library.size()-i
            for item in library.get(rank_item):
                if item not in item_ratings:
                    item_ratings[item] = 0
            attribute_vals = {}
        elif init_type == 'properties':
            attribute_vals = info
            item_ratings = {item:get_attribute_rating(item,attribute_vals) for item in library.get(rank_item)}
        return InexactRanking(name,desc,library,item_ratings,attribute_vals)
