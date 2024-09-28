import traceback, sys, re

from functools import wraps

import discord
import discord.ext
import asyncio

from discord.ext import commands
from accessify import protected, private

from bot_params import DEBUG_MODE, MAIN_COLOR, HELLCAT_ID

"""Класс контекста"""
class Ctx(commands.Context):
    pass

Ctx = commands.Context


"""Обработчик ошибок"""
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.reply(f"Не смог найти '**{error.argument}**'. Попробуй ещё раз.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Аргумент **'{error.param.name}**' не указан.")
    elif isinstance(error, commands.BadArgument):
        error_message = error.args[0]
        new_error_message = re.sub(r'Converting to "(.*)" failed for parameter "(.*)".',
                                   r'Ошибка преобразования в "**\1**" для параметра "**\2**".',
                                   error_message)
        await ctx.reply(new_error_message)
    else:
        if ctx.command:
            error(f"Игнорирую исключение в команде '{ctx.command}'")
        else:
            error(f"Игнорирую исключение. Не выполняемая команда '{ctx.message.content}'")
        if DEBUG_MODE:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

"""Декораторы"""
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
            
# Класс для пагинации сообщений
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
        from __init__ import bot
        
        self.bot = bot
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

    # Функция для проверки реакции
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

    # Асинхронная функция для пагинации
    async def paginate(self):
        self.ctx = await self.bot.get_context(await self.send_page())
        
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
        
    async def send_page(self):
        embed = discord.Embed(
            title=f"Страница {self.page_index + 1}/{len(self.pages)}",
            color=MAIN_COLOR,
            description=''
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
            if l in ['', ' ', '\n']:
                text.remove(l)
        
        
        for l in text:
            if len(''.join(page)) + len(l) < max_chars_per_page - 8:
                page.append(f"```js\n{l + " "}```")
            else:
                pages.append(page[:])
                page = []
        if page:
            pages.append(page)
            
        return pages
