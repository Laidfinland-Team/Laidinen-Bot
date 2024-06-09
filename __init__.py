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
from modules.logger.commands import error, info, warning, output
from _functions_base import *
from colorama import Fore, Style, Back
from discord.ext import commands
from pretty_help import PrettyHelp
from accessify import protected, private
from icecream import ic
from datetime import datetime
import os


match os.name:
    case "nt":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + "\TOKEN.py"
    case "posix":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + '/TOKEN.py'


MAIN_COLOR = discord.Color.purple()

colorama.init(autoreset=True)
intents = discord.Intents.default()



bot = commands.Bot(command_prefix=PREFIX, help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"), intents=discord.Intents.all())


__spec = importlib.util.spec_from_file_location('AUTH', __AUTH_FILE_PATH)
__auth = importlib.util.module_from_spec(__spec)
__spec.loader.exec_module(__auth)
TOKEN = __auth.TOKEN

ic(discord.__version__)