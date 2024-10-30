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
import discord.types
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
    FORUM_CATEGORY_ID,
    HELLCAT_ID, 
    LAIDFIN_YOUTUBE_URL, 
    jerusalem_tz,
    
    MODERATOR_ROLE_ID
)


"""Раскомментируй строку ниже если используешь токен в файле TOKEN.py"""
# from TOKEN import TOKEN



# Инициализация colorama
colorama.init(autoreset=True)

# Инициализация get_member (_ds_func_base.py)
def fetch_member(member_id: int) -> discord.Member:
    ...
    
fetch_member = Fetch_member()


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


from discord.types.member import UserWithMember as __UserWithMember

def member_to_data(self) -> __UserWithMember:
    data = {
        'avatar': self.avatar,
        'nick': self.nick,
        'premium_since': self.premium_since.isoformat() if self.premium_since else None,
        'pending': self.pending,
        'permissions': self.permissions.value,
        'communication_disabled_until': self.communication_disabled_until.isoformat() if self.communication_disabled_until else None,
        'avatar_decoration_data': self.avatar_decoration_data.to_data() if self.avatar_decoration_data else None,
    }

    return data

#discord.Member.to_data = member_to_data

#from discord.types.threads import Thread as __ThreadPayload

def thread_to_data(self):
    data = {
        'id': self.id,
        'parent_id': self.parent_id,
        'owner_id': self.owner_id,
        'name': self.name,
        'type': self._type.value if self._type else None,
        'last_message_id': self.last_message_id,
        'rate_limit_per_user': self.slowmode_delay,
        'message_count': self.message_count,
        'member_count': self.member_count,
        'flags': self._flags,
        'applied_tags': list(self._applied_tags),  # Преобразуем array.array в список
        'thread_metadata': self._get_thread_metadata(),  # Предполагаем, что у вас есть метод для получения метаданных
    }

    if self.me is not None:
        data['member'] = self.me.to_data()  # Предполагаем, что у ThreadMember есть метод to_data
    else:
        data['member'] = None

    return data

discord.Thread.to_data = thread_to_data


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
