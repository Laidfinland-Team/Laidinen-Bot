import os
import sys

import importlib.util
import psycopg2
import sqlite3
import database.db as db
import discord
import asyncio
import colorama

#from TOKEN import TOKEN # Раскомментируйте эту строку если вы используете TOKEN.py внутри рабочей директории
from bot_params import PREFIX
from modules.logger.commands import Logger
from _functions_base import *
from colorama import Fore, Style, Back
from discord.ext import commands
from pretty_help import PrettyHelp
from accessify import protected, private
from icecream import ic
from datetime import datetime
import os

def info(message):
    log.info(message)
    
def error(message, e=None):
    log.error(message, e)

def warning(message):
    log.warning(message)

def output(message):
    log.output(message)


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