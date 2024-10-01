# 1. Стандартные библиотеки
import os
import sys
import json
import traceback
import sqlite3
import asyncio
import typing
import re

from datetime import datetime, timedelta, timezone
from functools import wraps

# 2. Внешние зависимости
import discord
import discord.ext
import discord.ext.commands
import psycopg2
import pytz
import colorama
import importlib.util

from colorama import Fore, Style, Back
from accessify import protected, private
from icecream import ic
from discord.ext import commands, tasks
from pretty_help import PrettyHelp

# 3. Внутренние модули проекта
import database.db as db

from _functions_base import *
from _discord_functions_base import *
from _discord_safety import *
from modules.logger import Logger
from bot_params import (
    PREFIX, 
    MAIN_COLOR, 
    DEBUG_MODE, 
    PROTECTED_MEMBERS_IDS,
    GUILD_ID,
    HELLCAT_ID, 
    LAIDFIN_YOUTUBE_URL, 
    jerusalem_tz
)


"""Раскомментируй строку ниже если используешь токен в файле TOKEN.py"""
# from TOKEN import TOKEN



# Инициализация colorama
colorama.init(autoreset=True)

# Инициализация intents
intents = discord.Intents.default()

# Инициализация логгера
log = Logger("log.log")

# Отключение логирования в режиме DEBUG_MODE
if not DEBUG_MODE:
    ic.disable()

# Логгинг сообщений

def security(message):
    log.security(message)
def system(message):
    log.system(message)

def info(message):
    log.info(message)

def error(message, error=None):
    log.error(message, error)

def warning(message):
    log.warning(message)

def output(channel, message):
    log.output(channel, message)






"""Инициализация бота"""
bot: commands.Bot = enabled_bot
bot.on_command_error = on_command_error
bot.add_check(mentions_check)


"""Загрузка токена"""
match os.name:
    case "nt":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'\TOKEN.py'
    case "posix":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'/TOKEN.py'

__spec = importlib.util.spec_from_file_location('AUTH', __AUTH_FILE_PATH)
__auth = importlib.util.module_from_spec(__spec)
__spec.loader.exec_module(__auth)
TOKEN = __auth.TOKEN


"""Вывод версии discord.py"""
print(Style.BRIGHT + f'Discord-py {discord.__version__}')
