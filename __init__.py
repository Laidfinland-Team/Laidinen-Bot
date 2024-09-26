import os
import sys

import importlib.util
import discord.ext.commands
import psycopg2
import sqlite3
import database.db as db
import discord
import asyncio
import colorama
import json


#from TOKEN import TOKEN # Раскомментируйте эту строку если вы используете TOKEN.py внутри рабочей директории
from bot_params import PREFIX
import discord.ext
from modules.logger.commands import Logger
from _functions_base import *
from colorama import Fore, Style, Back
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
from accessify import protected, private
from icecream import ic
from datetime import datetime
from functools import wraps
import os

def diapason(diapason: str, args_pos):
    def decorator(func):
        @wraps(func)
        async def wrapper(cog, ctx: Ctx, *args, **kwargs):
            diapason.split('-') 
            diapason = range(int(diapason[0]), int(diapason[1]) + 1)
                return await func(*args, **kwargs)
            else:
                return await ctx.send(f"Неверный аргумент. Допустимые значения: {', '.join(diapason)}")
        return wrapper
    return decorator

def info(message):
    log.info(message)
    
def error(message, e=None):
    log.error(message, e)

def warning(message):
    log.warning(message)

def output(channel, message):
    log.output(channel, message)

class Ctx(discord.ext.commands.Context):
    pass
Ctx = discord.ext.commands.Context

match os.name:
    case "nt":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'\TOKEN.py'
    case "posix":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'/TOKEN.py'



MAIN_COLOR = discord.Color.purple()

colorama.init(autoreset=True)
intents = discord.Intents.default()

log = Logger("log.log")


bot = commands.Bot(command_prefix=PREFIX, help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"), intents=discord.Intents.all())


__spec = importlib.util.spec_from_file_location('AUTH', __AUTH_FILE_PATH)
__auth = importlib.util.module_from_spec(__spec)
__spec.loader.exec_module(__auth)
TOKEN = __auth.TOKEN
HELLCAT_ID = 518516627629801494

ic(discord.__version__)