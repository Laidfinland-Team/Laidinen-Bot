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
import traceback
import os
import discord.ext

#from TOKEN import TOKEN # Раскомментируйте эту строку если вы используете TOKEN.py внутри рабочей директории
from bot_params import PREFIX
from modules.logger.commands import Logger
from _functions_base import *
from colorama import Fore, Style, Back
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
from accessify import protected, private
from icecream import ic
from datetime import datetime
from functools import wraps

DEBUG_MODE = True

def system(message):
    log.system(message)
    
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

class Paginator:
    def __init__(self, ctx: Ctx, pages, field_generator, timeout=60):
        """
        Инициализация класса Paginator.
        
        :param ctx: Контекст команды Discord.
        :param pages: Список страниц, каждая из которых представляет собой список элементов.
        :param field_generator: Функция для генерации полей embed. 
                                Должна принимать элемент и возвращать tuple (название, значение).
        :param timeout: Время ожидания реакции (в секундах).
        """
        self.ctx: Ctx = ctx
        self.author = ctx.author
        self.pages = pages
        self.page_index = 0
        self.field_generator = field_generator
        self.timeout = timeout
        self.msg: discord.Message = None

    @private
    async def send_page(self):
        embed = discord.Embed(
            title=f"Страница {self.page_index + 1}/{len(self.pages)}",
            description=f"Сообщений на странице: {len(self.pages[self.page_index])}",
            color=MAIN_COLOR
        )
        for item in self.pages[self.page_index]:
            name, value = self.field_generator(item)
            embed.add_field(name=name, value=value)

        if self.msg is None:
            self.msg = await self.ctx.send(embed=embed)
            await self.msg.add_reaction("⬅️")
            await self.msg.add_reaction("➡️")
            return self.msg
        else:
            return await self.msg.edit(embed=embed)

    def check_reaction(self, reaction: discord.Reaction, user):
        return user == self.author and str(reaction.emoji) in ["⬅️", "➡️"]
    
    @staticmethod
    def prepare_for_paginate(objects: dict[dict[dict]], content: str, formats: list[str], max_chars_per_page=6000) -> list[list[dict]]:
        pages = []
        current_page = []
        current_page_length = 0
        

        for obj in objects:
            obj = objects[obj]
            content = content.format(*[obj[f] for f in formats])
            thread_content = content  # Пример структуры треда
            thread_length = len(thread_content)

            # Если добавление текущего треда превысит лимит символов, создаем новую страницу
            if current_page_length + thread_length > max_chars_per_page:
                pages.append(current_page)
                current_page = []
                current_page_length = 0

            current_page.append(obj)
            current_page_length += thread_length

        # Добавляем последнюю страницу, если она не пуста
        if current_page:
            pages.append(current_page)

        return pages

    async def paginate(self):
        self.ctx = await bot.get_context(await self.send_page())
        
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=self.check_reaction)
                if str(reaction.emoji) == "➡️" and self.page_index < len(self.pages) - 1:
                    self.page_index += 1
                    await self.msg.remove_reaction(reaction, self.author)
                    await self.send_page()
                elif str(reaction.emoji) == "⬅️" and self.page_index > 0:
                    self.page_index -= 1
                    await self.msg.remove_reaction(reaction, self.author)
                    await self.send_page()
            except asyncio.TimeoutError:
                await self.msg.clear_reactions()
                break

class TextPaginator(Paginator):
    def __init__(self, ctx: Ctx, pages: list[list[str]], timeout=60):
        """
        Инициализация класса Paginator.
        
        :param ctx: Контекст команды Discord.
        :param pages: Список страниц, каждая из которых представляет собой список строк.
        :param timeout: Время ожидания реакции (в секундах).
        """
        super().__init__(ctx, pages, None, timeout)
        
    @private
    async def send_page(self):
        embed = discord.Embed(
            title=f"Страница {self.page_index + 1}/{len(self.pages)}",
            color=MAIN_COLOR
        )
        for item in self.pages[self.page_index]:
            embed.description += item + '\n'
        
        if self.msg is None:
            self.msg = await self.ctx.send(embed=embed)
            await self.msg.add_reaction("⬅️")
            await self.msg.add_reaction("➡️")
            return self.msg
        else:
            return await self.msg.edit(embed=embed)
        
    @staticmethod
    def prepare_for_paginate(text: str, max_chars_per_page=6000) -> list[list[str]]:
        page = []
        pages = []
        text = text.split('\n')
        for l in text:
            if l in ['', ' ']:
                text.remove(l)
        
        
        for l in text:
            if len(''.join(page)) + len(l) < max_chars_per_page:
                page.append(l)
            else:
                pages.append(page[:])
                page = []
        if page:
            pages.append(page)
            
        return pages

        
def is_hellcat():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
                
            if ctx.author.id == HELLCAT_ID:
                return await func(*args, **kwargs)
            else:
                return await ctx.reply("*У тебя нет прав*💔")
        return wrapper
    return decorator

match os.name:
    case "nt":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'\TOKEN.py'
    case "posix":
        __AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + r'/TOKEN.py'


MAIN_COLOR = discord.Color.purple()

colorama.init(autoreset=True)
intents = discord.Intents.default()

log = Logger("log.log")

if not DEBUG_MODE:
    ic.disable()

async def on_command_error(ctx: commands.Context, the_error):
    # Handle your errors here
    if isinstance(the_error, commands.MemberNotFound):
        await ctx.message.reply(f"Не смог найти '**{the_error.argument}**'. Попробуй ещё раз.")

    elif isinstance(the_error, commands.MissingRequiredArgument):
        await ctx.message.reply(f"Аргумент **'{the_error.param.name}**' не указан.")
        
    elif isinstance(the_error, commands.BadArgument):
                # Пример текста ошибки
        error_message = the_error.args[0]

        # Используем регулярное выражение для замены текста, не изменяя содержимое кавычек
        new_error_message = re.sub(r'Converting to "(.*)" failed for parameter "(.*)".',
                                   r'Ошибка преобразования в "**\1**" для параметра "**\2**".',
                                   error_message)
        
        await ctx.message.reply(new_error_message)
        
    else:
        if ctx.command is None:
            error(f"Ignoring exception. Not-executed command '{ctx.message.content}'")
        else:
            # All unhandled errors will print their original traceback
            error(f"Ignoring exception in command '{ctx.command}'")
            if DEBUG_MODE:
                traceback.print_exception(type(the_error), the_error, the_error.__traceback__, file=sys.stderr)


enabled_bot = commands.Bot(command_prefix=PREFIX, help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"), intents=discord.Intents.all())
enabled_bot.on_command_error = on_command_error

disabled_bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

bot: commands.Bot = enabled_bot

__spec = importlib.util.spec_from_file_location('AUTH', __AUTH_FILE_PATH)
__auth = importlib.util.module_from_spec(__spec)
__spec.loader.exec_module(__auth)
TOKEN = __auth.TOKEN
HELLCAT_ID = 518516627629801494
LAIDFIN_YOUTUBE_URL = 'https://www.youtube.com/@Laidfin'

print(Style.BRIGHT + f'Discord-py {discord.__version__}')