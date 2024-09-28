import os as _os
import re

from functools import wraps
from discord.ext import commands
from discord import Message, Embed
from decorator import decorator
from icecream import ic
from modules.logger.commands import Logger

from pythonlangutil.overload import Overload, signature

from typing import overload, Union

from multipledispatch import dispatch

log = Logger("log.log")
class Ctx(commands.Context):
    pass
Ctx = commands.Context

class Cog(commands.Cog):
    pass
Cog = commands.Cog

class FormatEmbed(Embed):
    def __init__(self, title, description=None, color=None):
        super().__init__(title=title, description=description, color=color)  
        
    def format(self, *args, **kwargs):
        # Количество подстановочных мест в заголовке
        title_args_count = self.title.count('{}')
        
        # Форматируем заголовок, передавая соответствующее количество аргументов
        if title_args_count > 0:
            self.title = self.title.format(*args[:title_args_count])

        # Количество подстановочных мест в описании
        description_args_count = self.description.count('{}')
        
        # Форматируем описание, передавая оставшиеся аргументы
        if description_args_count > 0:
            self.description = self.description.format(*args[title_args_count:title_args_count + description_args_count])
        
        return self
class Diapason:
    def __init__(self, diapason_str):
        self.diapason_str = diapason_str
        diapason_match = re.match(r'(-?\d*\.?\d*)-(-?\d*\.?\d*)', diapason_str)
        if diapason_match:
            start_str, end_str = diapason_match.groups()
            if '.' in start_str or '.' in end_str:
                self.type = float
                self.start = float(start_str)
                self.end = float(end_str)
            else:
                self.type = int
                self.start = int(start_str)
                self.end = int(end_str)
        else:
            raise ValueError(f"Invalid diapason format: {diapason_str}")
    
    @property
    def width(self):
        return self.end - self.start
    
    @property
    def bounds(self):
        return self.start, self.end
    
    def __call__(self, value):
        if type(value) is not self.type:
            return False
        else:
            return self.start <= value <= self.end
        
        
    def __repr__(self):
        return f"{self.__class__.__name__}:{self.diapason_str}"
    
    def __str__(self):
        return f"Diapason({self.diapason_str})"
    
    def __eq__(self, other):
        if isinstance(other, Diapason):
            return (self.start, self.end) == (other.start, other.end)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        if isinstance(other, Diapason):
            return (self.start, self.end) < (other.start, other.end)
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, Diapason):
            return (self.start, self.end) <= (other.start, other.end)
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Diapason):
            return (self.start, self.end) > (other.start, other.end)
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, Diapason):
            return (self.start, self.end) >= (other.start, other.end)
        return NotImplemented


def diapason(diapason_str: str, args_names: list) -> callable:
    diapason_obj = Diapason(diapason_str)
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            for key, value in kwargs.items():
                if key in args_names:
                    if not diapason_obj(tpif(value)):
                        return await ctx.message.reply(
                            f"Неверный аргумент '**{key}**'. Допустимые значения {"**целые числа**" if diapason_obj.type is int else ""}: **{diapason_obj.start}-{diapason_obj.end}**"
                        )

            return await func(*args, **kwargs)

        return wrapper
    return decorator

def arguments_required():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            if len(args) < (2 if func.__qualname__.split('.')[0] == func.__name__ else 3):
                return await ctx.message.reply("Необходимо указать аргументы😶")
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def is_async():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def disabled():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            return await ctx.message.reply("Команда временно отключена🔒")
        return wrapper
    return decorator


def cls():
    _os.system('cls')
    
    

def trys(func: callable, *args, **kwargs) -> callable:
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log.error("`trys` error:", e)
        return 0
    
async def atrys(func: callable, *args, **kwargs) -> callable:
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        log.error("`atrys` error:",e)
        return 0

    

def tryParseString(string):
    try:
        return str(string)
    except ValueError:
        return False
    
def tps(string):
    return tryParseString(string)
    

def tryParseInt(string):
    try:
        return int(string)
    except ValueError:
        return False
    
def tpi(string):
    return tryParseInt(string)
    
    
def tryParseFloat(string):
    try:
        return float(string)
    except ValueError:
        return False
    
def tpf(string):
    return tryParseFloat(string)

def tryParseIntFloat(string):
    """Try parsing integer, otherwise float."""
    try:
        return int(string)
    except ValueError:
        return tpf(string)
    
def tpif(string):
    return tryParseIntFloat(string)
    
def check_for_numbers(number):
    number = type(number)
    result = True if number is int or number is float else False
    return result

def cfn(number):
    return check_for_numbers(number)

def check_for_string(string):
    string = type(string)
    result = True if string is str else False
    return result

def cfs(string):
    return check_for_string(string)


def check_for_bool(boolean):
    boolean = type(boolean)
    result = True if boolean is bool else False
    return result

def cfb(boolean):
    return check_for_bool(boolean)


def check_for_custom_string(args, arg):
    result = True if arg in args else False
    return result

def cfcs(args, arg):
    return check_for_custom_string(args, arg)


def hide (string):
    return string.replace(string, '■' * len(string))

