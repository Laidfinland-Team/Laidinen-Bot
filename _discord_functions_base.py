import traceback, sys, re
import typing
import random
import datetime

from functools import wraps

import discord
import discord.ext
import asyncio
import textwrap


from discord.ext import commands
from accessify import protected, private
from dataclasses import dataclass
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps, ImageFont

from bot_params import (
    DEBUG_MODE, 
    MAIN_COLOR, 
    HELLCAT_ID, 
    MODERATOR_ROLE_ID, 
    GUILD_ID, 
    jerusalem_tz
)
from modules.logger import Logger
from _functions_base import *

log = Logger("log.log")

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
    elif isinstance(error, commands.CommandNotFound):
        log.error(f"Command '{ctx.message.content}' not find. Channel: {ctx.channel}")
    elif isinstance(error, commands.CheckFailure):
        log.error(f"Check failure. Command: {ctx.command} Channel: {ctx.channel}")
    elif isinstance(error, commands.MessageNotFound):
        log.error(f"Message not found. Channel: {ctx.channel}")
    elif isinstance(error, discord.errors.Forbidden) and error.code == 50013:
        log.error("Missing permissions")
    else:
        if ctx.command:
            log.error(f"Ignoring exception in command' {ctx.command}'. Channel: {ctx.channel}")
        else:
            log.error(f"Ignoring exception. Not executable command '{ctx.message.content}'. 'Channel: {ctx.channel}")
            
        if DEBUG_MODE:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
async def on_check_failure(self, ctx, error):
    await ctx.reply("Этого пользователя нельзя обижать :shield: ")
    return False

"""Декораторы"""
def is_hellcat():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            if ctx is False:
                return await func(*args, **kwargs)
            
            elif ctx.author.id == HELLCAT_ID:
                return await func(*args, **kwargs)
            
            else:
                return await ctx.reply("*У тебя нет прав*💔")
        return wrapper
    return decorator

def is_moder_or_admin():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            if ctx is False:
                return await func(*args, **kwargs)
            
            elif MODERATOR_ROLE_ID in [r.id for r in ctx.author.roles] or ctx.author.guild_permissions.administrator:
                return await func(*args, **kwargs)
            
            else:
                return await ctx.reply("*У тебя нет прав*💔")
        return wrapper
    return decorator

def is_disabled():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            return await ctx.message.reply("Команда временно отключена🔒")
        return wrapper
    return decorator

def is_on_maintenance():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[0] if func.__qualname__.split('.')[0] == func.__name__ else args[1]
            return await ctx.message.reply("Для это команды проводятся технические работы🔧")
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


"""Функции"""
class DiscordFunctions:
    def __init__(self):
        
        
        self.guild_id = GUILD_ID
        self.bot = None
        
        
class Fetch_member(DiscordFunctions):
    def __init__(self):
        super().__init__()
        
    async def __call__(self, member_id):
        
        from __init__ import bot
        self.bot = bot
        
        guild: discord.Guild = self.bot.get_guild(self.guild_id)
        try:
            member: discord.Member = await guild.fetch_member(member_id)
        except discord.errors.NotFound:
            return None
        return member

"""Класс для пагинации сообщений"""
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
                await atrys(self.msg.clear_reactions)
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
    
"""Классы для создания репортов"""

@dataclass
class FakeMessage():
    """ Класс, позволяющий создать копию discord.Message для обработки отрисовщиком скриншотов """

    content: str = None
    reactions: typing.List[discord.Reaction] = ()
    mentions: typing.List[discord.Member] = ()
class Report():
    """ Класс для создания и отправки сообщения в канал для модераторов """

    def __init__(self, member: typing.Optional[discord.Member], alert_channel: discord.TextChannel = None):
        
        self.alert_channel = alert_channel

        offset = datetime.timedelta(hours=3)
        self.tz = jerusalem_tz


        self.id = random.randint(1, 1000000)
        self.member = member
        self.img_filename = f"{self.id}.png"
        self.img_file: discord.File = None 
        self.attachments: list[discord.File] = [] 
        self.embeds: list[discord.Embed] = []


        self.time = datetime.datetime.now(tz=self.tz).strftime("%d %B - %H:%M")
        self._title = ""
        self._desc = ""
        self.color = discord.Colour.random()

    @property
    def desc(self):
        return self._desc
    
    @desc.setter
    def desc(self, args):
        try:
            name = args[0]
            value = args[1]
        except:
            log.error("Invalid arguments for desc setter")
        else:
            self._desc += f"\n**{name}:** {value}"

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = title

    @private
    def _get_main_embed(self):
        embed = discord.Embed(title=self.title, description=self.desc, color=self.color)
        embed.set_image(url=f"attachment://{self.img_filename}")
        return embed

    async def create_img(self, messages):

        TEXT_COLOR = discord.Color.light_embed().to_rgb()
        DATE_COLOR = discord.Color.light_gray().to_rgb()

        FONT_SIZE = 24

        SMALL_FONT = ImageFont.truetype("cogs/delcog/NotoSans-Regular.ttf", FONT_SIZE - 10) # Уменьшенный шрифт (дата отправки)
        NORMAL_FONT = ImageFont.truetype("cogs/delcog/NotoSans-Regular.ttf", FONT_SIZE) # Обычный шрифт (текст)
        BOLD_FONT = ImageFont.truetype("cogs/delcog/NotoSans-Medium.ttf", FONT_SIZE) # Жирный шрифт (никнейм)

        BACKGROUND_COLOR = (54, 57, 63)

        # Контент = аватарка + никнейм + текст + всё остальное, короче всё кроме фона входит в блок контента

        CONTENT_X = 15  # Расстояние от левого края изображения до контента
                        # Изменять для смещения всего содержимого влево/вправо

        CONTENT_Y = 10  # Расстояние от верхнего края изображения до контента
                        # Изменять для смещения всего содержимого вверх/вниз

        DISTANCE_BETWEEN_AVATAR_AND_TEXTBOX = 90 # Расстояние между левым краем аватарки и текстом
        DISTANCE_BETWEEN_NAME_AND_DATE = 5 # Расстояние между никнеймом и датой отправки
        ONE_MESSAGE_HEIGHT = 40 # Высота одного однострочного сообщения

        TEXTBOX_X = CONTENT_X + DISTANCE_BETWEEN_AVATAR_AND_TEXTBOX # Расстояние от левого края изображения до текста
        TEXTBOX_Y = CONTENT_Y - 2 # Минус чтобы выровнять в одну линию текст и аватарку

        for i, message in enumerate(messages): # Вложения на скриншоте игнорируются, на их месте становится надпись [Вложение]
            if message.attachments or message.embeds:
                if len(message.attachments) == 1 or len(message.embeds) == 1:
                    messages = list(messages[:i+1]) + [FakeMessage(content = "[вложение]")] + list(messages[i+1:])
                elif len(message.attachments) > 1 or len(message.embeds) > 1:
                    messages = list(messages[:i+1]) + [FakeMessage(content = "[вложения]")] + list(messages[i+1:])


        height_increase = 40 * (len(messages)) + 5 # На каждое текстовое сообщение в высоту добавляется 40 пикселей + отступ в конце
        img_size = (750, 60 + height_increase) # Размер картинки


        img = Image.new(mode='RGB', size=img_size, color=BACKGROUND_COLOR) # Создание изображения
        img_draw = ImageDraw.Draw(img) # Объект для рисования на изображении


        messages_author: discord.Member = messages[0].author
        date = messages[0].created_at.strftime("%d.%m.%Y %H:%M")
        nickname = messages_author.display_name
        nickname_color = messages_author.color.to_rgb()


        member_avatar = Image.open(BytesIO(await messages_author.display_avatar.with_size(64).read()))
        mask = Image.open("cogs/delcog/mask.png").convert('L')
        member_avatar = ImageOps.fit(member_avatar, mask.size, centering = (0.5, 0.5)) # Округливание аватарки


        if nickname_color == discord.Color.default().to_rgb(): # Если цвет ника стандартный
            nickname_color = TEXT_COLOR


        img_draw.text((TEXTBOX_X, TEXTBOX_Y), nickname, nickname_color, font = BOLD_FONT) # рисование никнейма
        #img_draw.text((TEXTBOX_X + (len(without_spaces(nickname)) * (FONT_SIZE - 4)) + nickname.count(" ") * 2, TEXTBOX_Y + 10), date, DATE_COLOR, font = SMALL_FONT) # рисование даты
        img.paste(member_avatar, (CONTENT_X, CONTENT_Y), mask = mask) # рисование аватарки


        previous_position = TEXTBOX_Y - 5 # Позиция по Y предыдущего сообщения. 

        for message in messages:
            message_text = textwrap.fill(message.content, width = 40, replace_whitespace = False)

            for member in message.mentions: # заменяет упоминание на @никнейм
                message_text = re.sub(f"<@{member.id}>", f"@{member.display_name}", message_text)

            strings_amount = len(message_text.splitlines())

            if strings_amount > 1:
                img_size = (img_size[0], img_size[1] + ONE_MESSAGE_HEIGHT * strings_amount - ONE_MESSAGE_HEIGHT - 10)
                old_img = img
                img = Image.new(mode = 'RGB', size = img_size, color = BACKGROUND_COLOR)
                img_draw = ImageDraw.Draw(img)
                img.paste(old_img)

            string_pos = previous_position + ONE_MESSAGE_HEIGHT

            if message.content:

                color = TEXT_COLOR
                if isinstance(message, FakeMessage): 
                    color = DATE_COLOR

                img_draw.multiline_text(xy = (TEXTBOX_X, string_pos), 
                                        text = message_text, 
                                        fill = color, 
                                        font = NORMAL_FONT,
                                        spacing = ONE_MESSAGE_HEIGHT / 3)
                

            previous_position = previous_position + ONE_MESSAGE_HEIGHT * strings_amount


        return img

    async def upload_all(self, messages):
        await self.upload_attachments(messages)
        await self.upload_embeds(messages)

    async def upload_attachments(self, messages):
        for message in messages:
            self.attachments.extend([discord.File(fp = BytesIO(await a.read()), filename = a.filename) for a in message.attachments])
            
    async def upload_embeds(self, messages: list[discord.Message]):
        for message in messages:
            for e in message.embeds:
                self.embeds.append(e)
                
    def set_image(self, img):
        if type(img) == list:
            main_img = Image.new(mode="RGB", size=(750, sum([image.height for image in img])))
            height = 0
            
            for image in img:
                main_img.paste(image, (0, height))
                height += image.height
            else:
                img = main_img
                
        if img:
            imgb = BytesIO()
            img.save(imgb, format = "PNG")
            imgb.seek(0)
            self.img_file = discord.File(fp = imgb, filename = self.img_filename)

    async def send(self, output_channel: discord.TextChannel=None):
        output_channel = self.alert_channel if output_channel is None else output_channel
        main_embed = self._get_main_embed()
        sub_embeds = []

        if self.attachments:
            for i, a in enumerate(self.attachments):
                e = discord.Embed(description = f"Вложение {i+1}", color = self.color)
                e.set_image(url = f"attachment://{a.filename}")
                sub_embeds.append(e)
            #sub_embeds.extend([discord.Embed(url = f"attachment://{a.filename}", description = f"Вложение {i}", color = self.color) for i, a in enumerate(self.attachments)])
        if self.embeds:
            sub_embeds.extend(*self.embeds)
        
        
        if type(output_channel) is not discord.Thread:
            report_msg = await output_channel.send(file = self.img_file, embed = main_embed)
            return report_msg
        else:
            if self.attachments or self.embeds:
                message = await output_channel.send(embeds = sub_embeds, files = self.attachments)

"""Класс для удобного форматирования в embed"""
class FormatEmbed(Embed):
    def __init__(self, title, description=None, color=None):
        super().__init__(title=title, description=description, color=color)  
        
    def format(self, *args: list[str], **kwargs: dict[str:object]):
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
    