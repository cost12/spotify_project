import dominate.tags as tags
#import dominate.util as util
from typing import Any, Callable
import pandas as pd

def identity(x:pd.Series):
    return x

def apply(x:pd.Series, fun:Callable) -> pd.Series:
    return x.apply(fun)

class Table:

    def __init__(self,
                 name:str,
                 headers:list[str],
                 data_function:Callable[[Any],dict[str,Any]],*,
                 column_alignments:dict[str,str]|None=None,
                 header_functions:dict[str,str]|None=None,
                 column_functions:dict[str,Callable[[str],str]]|None=None,
                 sort_functions:dict[str,Callable[[Any],float]]|None=None):
        self.name = name
        self.headers = headers
        self.data_function = data_function
        self.column_alignments = column_alignments if column_alignments is not None else dict[str,str]()
        self.header_functions =  header_functions  if header_functions  is not None else dict[str,str]()
        self.column_functions =  column_functions  if column_functions  is not None else dict[str,Callable[[str],str]]()
        self.sort_functions =    sort_functions    if sort_functions    is not None else dict[str,Callable[[Any],float]]()

    def to_html(self, data_source:list[Any], sort_column:str='', reverse:bool=False,*,user_id:str='',ranking_id:str='') -> tags.div:
        #data = {}
        data = []
        for x in data_source:
            #data[header] = self.data_functions[header](data_source)
            data.append(self.data_function(user_id, ranking_id, x))
        df = pd.DataFrame(data, columns=self.headers)
        if sort_column in self.headers:
            df = df.sort_values(by=sort_column, axis=0, key=lambda x: apply(x, self.sort_functions.get(sort_column,identity)), ascending=reverse)
        return table_to_html(df, self.name, user_id, column_alignments=self.column_alignments, header_functions=self.header_functions, column_functions=self.column_functions)

def table_to_html(data:pd.DataFrame, class_name:str, user_id:str,*, column_alignments:dict[str,str]|None=None, header_functions:dict[str,str]|None=None, column_functions:dict[str,Callable[[Any],str]]|None=None) -> tags.div:
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
                                tags.td(datum, _class=column_alignments[header], onclick=column_functions[header](user_id,datum))
                            else:
                                tags.td(datum, onclick=column_functions[header](user_id,datum))
                        else:
                            if header in column_alignments:
                                tags.td(datum, _class=column_alignments[header])
                            else:
                                tags.td(datum)
    return table

def create_table(name:str,headers:list[str],data_function:Callable[[Any],dict[str,Any]],*,right_aligned:list[str]=[],column_sorts:bool=True,column_functions:dict[str,Callable[[str],str]]|None=None,sort_functions:dict[str,Callable[[Any],float]]|None=None):
    column_alignments = {header:'table-right' for header in right_aligned}
    if column_sorts:
        header_functions = {header:f'sortTable("{name}","{header}")' for header in headers}
    else:
        header_functions = None
    return Table(name,headers,data_function,column_alignments=column_alignments,header_functions=header_functions,column_functions=column_functions,sort_functions=sort_functions)

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