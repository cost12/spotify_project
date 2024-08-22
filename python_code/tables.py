import dominate
import dominate.tags as tags
#import dominate.util as util
from typing import Any, Callable
import pandas as pd

class Table:

    def __init__(self, 
                 name:str, 
                 headers:list[str], 
                 column_alignments:dict[str,str], 
                 header_functions:dict[str,str], 
                 column_functions:list[Callable[[str],str]], 
                 sorts:dict[str,Callable[[Any],float]], 
                 data_funcs:dict[str,Callable[[Any],str]],*,initial_sort:str|None=None,reverse=False):
        self.name = name
        self.headers = headers
        self.column_align = column_alignments
        self.header_functions = header_functions
        self.column_functions = column_functions
        self.sort_functions = sorts
        self.data_functions = data_funcs
        if initial_sort is not None:
            self.sort_column = initial_sort
        else:
            self.sort_column = headers[0]
        self.reverse = reverse

    def set_sort(self, sort:str) -> None:
        if sort != self.sort_column:
            self.reverse = not self.reverse
        self.sort_column = sort

    def to_html(self, data_source) -> tags.div:
        data = {}
        for i,header in enumerate(self.headers):
            data[header] = self.data_functions[header](data_source)
        df = pd.DataFrame(data, columns=self.headers)
        df = df.sort_values(by=self.sort_column, axis=0, key=lambda x: self.sort_functions[self.sort_column](x), ascending=self.reverse)
        return table_to_html(df, self.name, self.column_align, self.header_functions, self.column_functions)

def table_to_html(data:pd.DataFrame, class_name:str, column_alignments:dict[str,str]|None=None, header_functions:dict[str,str]|None=None, column_functions:dict[str,Callable[[Any],str]]|None=None) -> tags.div:
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
                        if header in column_alignments:
                            tags.th(header, _class=column_alignments[header], onclick=header_functions[header])
                        else:
                            tags.th(header, onclick=header_functions[header])
                    else:
                        if header in column_alignments:
                            tags.th(header, _class=column_alignments[header])
                        else:
                            tags.th(header)
            for index,row in data.iterrows():
                with tags.tr():
                    for datum,header in zip(row,data.columns):
                        if header in column_functions:
                            tags.td(datum, on_click=column_functions[header](datum))
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
                  {'two':'right-align','three':'right-align'},
                  {'one':"sortTable('one')",'two':"sortTable('two')",'three':"sortTable('three')"},
                  {'one':lambda x: f'sendTo("{x}")'},
                  {'one':lambda x:x,'two':lambda x:x.lower(),'three':lambda x:(x-3)**2},
                  {'one':lambda x: x.nums(), 'two':lambda x: x.chars(), 'three':lambda x: x.nums2()})
    html = table.to_html(data)
    print(html.render())

if __name__=="__main__":
    test()