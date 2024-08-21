import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from utils import Scheduler, subsrting_from_to, adjust_range, ms_to_str

def test_get(sched:Scheduler, count:int, expected:float):
    actual = sched.get_val(count)
    assert expected == actual

def test_sched():
    sched = Scheduler([(10,5),(5,10),(0,15),(20,3),(50,1)])
    test_get(sched, 3, 15)
    test_get(sched, 7, 10)
    test_get(sched, 12, 5)
    test_get(sched, 25, 3)
    test_get(sched, 100, 1)

def test_str(string, fr, to, expected):
    actual = subsrting_from_to(string,fr,to)
    assert actual == expected

def test_substr():
    test_str('spotify-long-term','-','-', 'long')
    test_str('spotify-long-term','-l','g-', 'on')

def test_range(dic:dict,min_val,max_val,expected):
    actual = adjust_range(dic,min_val,max_val)
    if actual != expected:
        print(f"expected: {expected} got: {actual}")
    assert actual==expected

def test_adjust_range():
    dict1 = {"one":1,"two":2,"three":3}
    dict2 = {'a':1,'b':1,'c':1}
    test_range(dict1,0,6, (3,-3))
    test_range(dict1,5,6, (0.5,4.5))
    test_range(dict2,0,2, (1,0))
    test_range(dict2,10,20, (1,14))

def test_ms(ms:int,expected):
    actual = ms_to_str(ms)
    if actual != expected:
        print(f'expected: {expected} got: {actual}')
    assert actual == expected

def test_ms_to_str():
    test_ms(10,'0:00.010')
    test_ms(1010,'0:01.010')
    test_ms(305001,'5:05.001')
    test_ms(7200000,'2:00:00.000')

def test():
    test_sched()
    test_substr()
    test_adjust_range()
    test_ms_to_str()

if __name__=="__main__":
    test()