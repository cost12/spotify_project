from typing import Any
import math

def to_playlists(playlists:dict[str,Any]) -> dict[str,Any]:
    """
    Extracts information about playlists from a dictionary
    """
    newp = list[dict[str,Any]]()

    keys = ['id','description','name','tracks']
    for p in playlists:
        new = {}
        for key in keys:
            new[key] = p[key]
        new['owner'] = p['owner']['display_name']
        new['followers'] = p['followers']['total']
        new['url'] = p['external_urls']['spotify']
        newp.append(new)

    return newp

def subsrting_from_to(string:str, from_str:str, to_str:str) -> str:
    start = string.index(from_str)+len(from_str)
    end = string.index(to_str,start)
    return string[start:end]

def adjust_range(ratings:dict[Any,float], min_val:float, max_val:float,*,change_vals=False) -> tuple[float,float]:
    if min_val >= max_val:
        return 1,0
    rating_min = min(ratings.values())
    rating_max = max(ratings.values())
    rating_range = rating_max-rating_min
    if abs(rating_range) < 0.00001:
        mult = 1
        add = (max_val+min_val)/2 - rating_max
    else:
        mult = (max_val-min_val)/(rating_range)
        add = max_val - rating_max*mult
    if change_vals:
        ratings.update({item:val*mult+add for item,val in ratings.items()})
    return mult,add

def ms_to_str(ms:int) -> str:
    seconds = ms//1000
    ms -= seconds*1000
    minutes = seconds//60
    seconds -= minutes*60
    hours = minutes//60
    minutes -= hours*60
    answer = ''
    if hours > 0:
        answer += f'{hours}:{minutes:02d}:'
    else:
        answer += f'{minutes}:'
    answer += f'{seconds:02d}.{ms:03d}'
    return answer

class BinaryNode:

    def __init__(self, count=None, val=None, left=None, right=None):
        self.count = count
        self.val = val
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None
    
    def __repr__(self):
        return f"BinaryNode({self.count}, {self.val}, leaf={self.is_leaf()})"

class Scheduler:
    """
    Classed used for scheduling things like elo. Count is the number of times something 
    has occured value is the correct value to be used with that count

    TODO: balance the tree
    """
    def __init__(self, pairs:list[tuple[int,float]]):
        self.root = None
        for count,val in pairs:
            self.add(count,val)

    def print_tree(self):
        print(f"Scheduler with size={self.size()} height={self.height()}")
        print(f"root: {self.root} left={self.root.left} right={self.root.right}")
        self.__print_tree(self.root.left)
        self.__print_tree(self.root.right)

    def __print_tree(self, node:BinaryNode|None):
        if node is None:
            return
        print(f"node: {node} left={node.left} right={node.right}")
        self.__print_tree(node.left)
        self.__print_tree(node.right)

    def size(self):
        return self.__size(self.root)

    def __size(self, node:BinaryNode|None):
        if node is None:
            return 0
        return 1 + self.__size(node.left) + self.__size(node.right)

    def height(self):
        return self.__height(self.root)

    def __height(self, node:BinaryNode|None):
        if node is None:
            return 0
        return 1+max(self.__height(node.left),self.__height(node.right))

    def add(self, count:int, value:float) -> None:
        if self.root is None:
            self.root = BinaryNode(count,value)
        else:
            self.__add(self.root, count, value)

    def __add(self, node:BinaryNode, count:int, value:float) -> None:
        if count > node.count:
            if node.right is None:
                node.right = BinaryNode(count,value)
            else:
                self.__add(node.right, count, value)
        elif count < node.count:
            if node.left is None:
                node.left = BinaryNode(count,value)
            else:
                self.__add(node.left, count, value)
        else:
            node.val = value

    def get_val(self, count:int) -> float:
        if self.root is None:
            return None
        if count > self.root.count:
            if self.root.right is not None:
                val = self.__get_val(self.root.right, count)
                if val is not None:
                    return val
            return self.root.val
        elif count < self.root.count:
            return self.__get_val(self.root.left, count)
        else:
            return self.root.val

    def __get_val(self, node:BinaryNode|None, count:int) -> float:
        if node is None:
            return None
        if count > node.count:
            if node.right is not None:
                val = self.__get_val(node.right, count)
                if val is not None:
                    return val
            return node.val
        elif count < node.count:
            return self.__get_val(node.left, count)

class EloSystem:
    
    def __init__(self, initial_ratings:dict):
        self.elo_schedule = Scheduler([(0,32),(10,24),(25,16),(50,10)])
        self.ratings = initial_ratings
        self.num_comparisons = {item:0 for item in initial_ratings.keys()}

    def get_rating(self, item) -> float:
        return self.ratings[item]
    
    def get_comparisons(self, item) -> int:
        return self.num_comparisons[item]
    
    def max_elo(self) -> float:
        return max(self.ratings.values())
    
    def min_elo(self) -> float:
        return min(self.ratings.values())
    
    def get_rank(self, item) -> int:
        items = list(self.ratings.keys())
        items.sort(key=lambda x: self.get_rating(x), reverse=True)
        index = items.index(item)
        i = index-1
        while i >= 0 and items[i] == items[index]:
            i -= 1
        return i+2
    
    def get_order(self) -> list:
        items = list(self.ratings.keys())
        items.sort(key=lambda x: self.get_rating(x), reverse=True)
        return items
    
    def get_items(self) -> list:
        return list(self.ratings.keys())

    def expected_outcome(self, item1, item2) -> float:
        ra = self.get_rating(item1)
        rb = self.get_rating(item2)
        return 1/(1+math.pow(10,(rb-ra)/480))
    
    def get_kvalue(self, item) -> int:
        return self.elo_schedule.get_val(self.num_comparisons[item])
    
    def add_result(self, item1, item2, result1):
        result2 = 1-result1
        expected1 = self.expected_outcome(item1,item2)
        expected2 = 1-expected1
        k1 = self.get_kvalue(item1)
        k2 = self.get_kvalue(item2)
        self.ratings[item1] += k1*(result1-expected1)
        self.ratings[item2] += k2*(result2-expected2)
        self.num_comparisons[item1] += 1
        self.num_comparisons[item2] += 1

    def adjust_rating(self, item, amount):
        self.ratings[item] += self.get_kvalue(item)*amount
        self.num_comparisons[item] += 1