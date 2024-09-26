import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))

from functools import wraps
from __init__  import *
import re
from abc import ABC, ABCMeta, abstractmethod

from functools import wraps

def c():
    def d(func):
        # Печатаем принадлежность метода классу
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Метод принадлежит классу: {func.__qualname__.split('.')[0]}")
            print(111)
            return func(*args, **kwargs)
        return wrapper
    return d

class a:
    def __init__(self):
        pass
    
    @c()
    def b(self):
        print(123)
        
obj = a()
obj.b()
