import dominate
import dominate.tags as tags
#import dominate.util as util
from typing import Any, Callable
import pandas as pd

def identity(x):
    return x

class Table:

    def __init__(self,
                 name:str,
                 headers:list[str],
                 data_function:Callable[[list[Any]],list[str]],*,
                 column_alignments:dict[str,str]|None=None,
                 header_functions:dict[str,str]|None=None,
                 column_functions:list[Callable[[str],str]]|None=None,
                 sort_functions:dict[str,Callable[[Any],float]]|None=None,
                 initial_sort:str|None=None,reverse=False):
        self.name = name
        self.headers = headers
        self.data_function = data_function
        self.column_alignments = column_alignments if column_alignments is not None else dict[str,str]()
        self.header_functions =  header_functions  if header_functions  is not None else dict[str,str]()
        self.column_functions =  column_functions  if column_functions  is not None else list[Callable[[str],str]]()
        self.sort_functions =    sort_functions    if sort_functions    is not None else dict[str,Callable[[Any],float]]()
        self.sort_column =       initial_sort      if initial_sort      is not None else headers[0]
        self.reverse = reverse

    def set_sort(self, sort:str) -> None:
        if sort != self.sort_column:
            self.reverse = not self.reverse
        self.sort_column = sort

    def to_html(self, data_source:list[Any]) -> tags.div:
        #data = {}
        data = []
        for i,header in enumerate(self.headers):
            #data[header] = self.data_functions[header](data_source)
            data.append(self.data_function(data_source))
        df = pd.DataFrame(data, columns=self.headers)
        df = df.sort_values(by=self.sort_column, axis=0, key=lambda x: self.sort_functions.get(self.sort_column,identity)(x), ascending=self.reverse)
        return table_to_html(df, self.name, column_alignments=self.column_alignments, header_functions=self.header_functions, column_functions=self.column_functions)

def table_to_html(data:pd.DataFrame, class_name:str,*, column_alignments:dict[str,str]|None=None, header_functions:dict[str,str]|None=None, column_functions:dict[str,Callable[[Any],str]]|None=None) -> tags.div:
    if column_alignments is None:
        column_alignments = {}
    if header_functions is None:
        header_functions = {}
    if column_functions is None:
        column_functions = {}
    
    table = tags.div(_class=f"table {class_name}")
    with table:
        with tags.table(_class=class_name):
            with tags.tr():
                for i,header in enumerate(data.columns):
                    if header in header_functions:
                        tags.th(header, onclick=header_functions[header])
                    else:
                        tags.th(header)
            for index,row in data.iterrows():
                with tags.tr():
                    for datum,header in zip(row,data.columns):
                        if header in column_functions:
                            if header in column_alignments:
                                tags.td(datum, _class=column_alignments[header], onclick=column_functions[header](datum))
                            else:
                                tags.td(datum, onclick=column_functions[header](datum))
                        else:
                            if header in column_alignments:
                                tags.td(datum, _class=column_alignments[header])
                            else:
                                tags.td(datum)
    return table


def test():
    class TestData:
        def __init__(self):
            pass
        def nums(self):
            return [1,4,3,5,2]
        def nums2(self):
            return [1,3,8,4,0]
        def chars(self):
            return ['a','A','z','X','m']

    data = TestData()
    table = Table('test',
                  ['one','two','three'],
                  {'one':lambda x: x.nums(), 'two':lambda x: x.chars(), 'three':lambda x: x.nums2()},
                  column_alignments={'two':'right-align','three':'right-align'},
                  header_functions={'one':"sortTable('one')",'two':"sortTable('two')",'three':"sortTable('three')"},
                  column_functions={'one':lambda x: f'sendTo("{x}")'},
                  sort_functions={'one':lambda x:x,'two':lambda x:x.lower(),'three':lambda x:(x-3)**2})
    html = table.to_html(data)
    print(html.render())

if __name__=="__main__":
    test()