import discord
from discord.ext import commands

import random
import json

from __init__ import *

ADMIN_MODE = False # Включение/выключение отправки в +1 и featured одной реакцией администратора.
ADMIN_MODE_WITH_REACT = True # Включение/выключение отправки в +1 и featured одной реакцией администратора с помощью реакции.
ADMIN_MODE_REACTION = 'B_application'

DB_DIR = r"light_databases\featured_messages.json"

# ID канала для отправки сообщений в чат
CHAT_CHANNEL_ID = 1284969133242322986
# ID канала для отправки сообщений в мемы
MEME_FEATURED_CHANNEL_ID = 1286279718642913350
# ID канала для отправки сообщений в форум
FORUM_CHANNEL_ID = 1284968979340726273

# ID канала с мемами
MEME_CHANNEL_ID = [1156945713440247829, 1171017228683063307]

# Порог количества реакций для админов и пользователей
ADMIN_FORCE = 1
USER_FORCE = 6
PLUS_ONE_FORCE = 5

# Категории
FORUMS = 1180846730602889236
NOTCHATS = [1156902879530070107, 1221874671352545320, 1156945170969931847, 1273188151786995712]

# Эмодзи для реакций
ADMIN_EMOJI = 'AA_admin_featured'
SUPER_EMOJI = 'AA_super_featured'
USER_EMOJI = 'AA_featured'
PLUS_ONE_EMOJI = 'AA_plus_one'

# Цвета для эмбедов
ADMIN_COLOR = discord.Color.red()
SUPER_COLOR = discord.Color.green()
USER_COLOR = discord.Color.yellow()
PLUS_ONE_COLOR = discord.Color.blue()

class ReactionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.destination = None  # Место назначения (чат или форум)
        self.status = None  # Статус реакции (админская или пользовательская)
    
    def check_for_admin(self, member: discord.Member):
        # Проверяем, является ли пользователь администратором
        return member.guild_permissions.administrator
    
    def check_for_featured(self, message: discord.Message):
        # Проверяем, было ли сообщение уже добавлено в избранное
        with open(DB_DIR, "r") as f:
            featured_messages = json.load(f)
        return message.id in featured_messages
    
    def add_to_featured_file(self, message: discord.Message):
        # Добавляем сообщение в список избранных
        try:
            # Открываем файл и загружаем данные
            with open(DB_DIR, "r") as f:
                content = f.read()
                featured_messages = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            # Если файл не найден или поврежден, создаем новый список
            featured_messages = []
        
        # Добавляем ID сообщения в список, если его там еще нет
        if message.id not in featured_messages:
            featured_messages.append(message.id)
        
        # Сохраняем обновленный список в файл
        with open(DB_DIR, "w") as f:
            json.dump(featured_messages, f, indent=4)
            
    def remove_from_featured_file(self, message: discord.Message):
        # Удаляем сообщение из списка избранных
        with open(DB_DIR, "r") as f:
            featured_messages = json.load(f)
        
        # Удаляем ID сообщения из списка
        featured_messages.remove(message.id)
        
        # Сохраняем обновленный список в файл
        with open(DB_DIR, "w") as f:
            json.dump(featured_messages, f, indent=4)
            
    def check_for_admin_mode(self, message: discord.Message):
        if message.reactions and ADMIN_MODE_WITH_REACT:
            names_list = []
            # Собираем имена всех эмодзи в реакциях
            for reaction in message.reactions:
                for i in range(reaction.count):
                    names_list.append(reaction.emoji.name) if type(reaction.emoji) is not str else None
            state = False
            for reaction_name in names_list:
                if reaction_name == ADMIN_MODE_REACTION:
                    state = True
            if state:
                return True
            else:
                return ADMIN_MODE
    
    @commands.command()
    async def atf(self, ctx: commands.Context, *args: str):
        await self.add_to_featured(ctx, *args)
        
    @commands.command()
    async def add_to_featured(self, ctx: commands.Context, *args: str):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("У вас нет прав на использование этой команды")
            return

        # Последний аргумент - это статус (тип реакции)
        status = args[-1]
        message_urls = args[:-1]  # Все остальные аргументы - это ссылки на сообщения

        # Преобразуем статус в текстовый формат
        status = status.split(':')[1].replace(':', '') 

        if status == USER_EMOJI:
            status = 'user'
        elif status == ADMIN_EMOJI:
            status = 'admin'
        elif status == SUPER_EMOJI:
            status = 'super'
        elif status == PLUS_ONE_EMOJI:
            status = 'plus_one'

        successful_ids = []
        failed_ids = []

        for message_url in message_urls:
            try:
                channel_id = int(message_url.split('/')[-2].replace('/', ''))
                channel = bot.get_channel(channel_id)
                message_id = int(message_url.split('/')[-1])
                message: discord.Message = await channel.fetch_message(message_id)

                # Определяем место назначения
                if message.channel.id in MEME_CHANNEL_ID:
                    destination = 'meme'
                elif message.channel.category_id == FORUMS:
                    destination = 'forum'
                elif message.channel.category_id not in NOTCHATS:
                    destination = 'chat'
                else:
                    failed_ids.append(message_id)
                    continue

                if not self.check_for_featured(message):
                    await self.send_to(destination, message, status)
                    successful_ids.append(message_id)
                else:
                    self.remove_from_featured_file(message)
                    await self.send_to(destination, message, status)
                    successful_ids.append(message_id)

            except Exception as e:
                failed_ids.append(message_id)
                continue

        if successful_ids:
            await ctx.send(f"**Сообщения с ID {', '.join(map(str, successful_ids))} были добавлены в избранное**")
        
        if failed_ids:
            await ctx.send(f"**Не удалось добавить сообщения с ID {', '.join(map(str, failed_ids))} в избранное**")


                
    async def send_to(self, destination: str, message: discord.Message, status: str):
        # Отправляем сообщение в заданное место назначения
 
        if destination != 'meme':
            sub_title = "в чате" if destination == "chat" else "на форуме"
            match status:
                case 'user':
                    title = f"Избранное {sub_title}"
                    content = f"<:AA_featured:1284934932413550612>"
                    color=USER_COLOR
                case 'admin':
                    title = f"Избранное админами {sub_title}"
                    content = f"<:AA_admin_featured:1284934964445577308>"
                    color=ADMIN_COLOR
                case 'super':
                    title = f"УЛЬТРАБАЗА (чат)" if destination == 'chat' else "УЛЬТРАБАЗА (форум)"
                    content = f"<:AA_super_featured:1285255719398019284>"
                    color=SUPER_COLOR
                case 'plus_one':
                    title = f"Популярное мнение {sub_title}"
                    content = f"<:AA_plus_one:1171921902017712290>"
                    color=PLUS_ONE_COLOR
        else:
            match status:
                case 'user':
                    title = f"РАЗРЫВНАЯ"
                    content = f"<:AA_featured:1284934932413550612>"
                    color=USER_COLOR
                case 'admin':
                    title = f"Вы рассмешили админа"
                    content = f"<:AA_admin_featured:1284934964445577308>"
                    color=ADMIN_COLOR
                case 'super':
                    title = f"АХАХХАХАХАХАХАХАХХАХАХАХАХАХАХХАХАХАХАХАХАХХАХ"
                    content = f"<:AA_super_featured:1285255719398019284>"
                    color=SUPER_COLOR
                case 'plus_one':
                    title = f"ЖИЗА ЖИЗНЕННАЯ"
                    content = f"<:AA_plus_one:1171921902017712290>"
                    color=PLUS_ONE_COLOR
                    
        if message.content:
            # Check if the content is a single link
            if message.content.strip().startswith("http") and len(message.content.strip().split()) == 1:
                embed=None; content=f"# {content}\n{message.content if message.content else ''}\n-# [Видео]({message.content})\n-# Ссылка на сообщение:\n{message.jump_url}"
            else:
                embed = discord.Embed(
                    title=title,
                    description=f"{message.content}\n\n\n**Ссылка на сообщение: {message.jump_url}**",
                    color=color,
                ).set_author(name=message.author.display_name)
        else:
            embed = discord.Embed(
            title=title,
            description=f"**Ссылка на сообщение: {message.jump_url}**",
            color=color,
            ).set_author(name=message.author.display_name)
        
        if message.attachments:
            if not all([tt == -1 for tt in [message.attachments[0].url.find(t) for t in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']]]):
                embed.set_image(url=message.attachments[0].url)
            elif message.attachments[0].url.find('mp4') != -1 or message.attachments[0].url.find('mov') != -1:
                embed=None; content=f"# {content}\n{message.content if message.content else ''}\n-# [Видео]({message.attachments[0].url})\n-# Ссылка на сообщение:\n{message.jump_url}"
            else:
                embed.add_field(name="Вложение", value=f"[Ссылка на вложение]({message.attachments[0].url})")
        
        if destination == 'forum':
            # Отправляем в форум
            channel = self.bot.get_channel(FORUM_CHANNEL_ID)
            await channel.send(embed=embed, content=content)
            info(f"Message with ID {message.id} was sent to forum featured messages")
        elif destination == 'chat':
            # Отправляем в чат
            channel = self.bot.get_channel(CHAT_CHANNEL_ID)
            await channel.send(embed=embed, content=content)
            info(f"Message with ID {message.id} was sent to chat featured messages")
        elif destination == 'meme':
            # Отправляем в мемы
            channel = self.bot.get_channel(MEME_FEATURED_CHANNEL_ID)
            await channel.send(embed=embed, content=content)
            info(f"Message with ID {message.id} was sent to meme featured messages")
        
        # Если сообщение еще не в избранном, добавляем его
        if not self.check_for_featured(message):
            self.add_to_featured_file(message)
    
    @commands.Cog.listener()
    async def on_ready(self):
        # Событие при готовности бота
        info("Reactions cog is ready")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Обработка добавления реакции
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        # Определяем статус реакции (админская или пользовательская)
        if payload.emoji.name == USER_EMOJI:
            self.status = 'user'
        elif payload.emoji.name == ADMIN_EMOJI:
            self.status = 'admin'
        elif payload.emoji.name == SUPER_EMOJI:
            self.status = 'super'
        elif payload.emoji.name == PLUS_ONE_EMOJI:
            self.status = 'plus_one'
        
        # Определяем место назначения
        if channel.id in MEME_CHANNEL_ID:
            self.destination = 'meme'
        elif channel.category_id == FORUMS:
            self.destination = 'forum'
        elif channel.category_id not in NOTCHATS:
            self.destination = 'chat'
        
        # Если сообщение еще не в избранном
        if not self.check_for_featured(message):
            if self.destination:
                names_list = []
                # Собираем имена всех эмодзи в реакциях
                for reaction in message.reactions:
                    for i in range(reaction.count):
                        names_list.append(reaction.emoji.name) if type(reaction.emoji) is not str else None
                # Проверяем условия для пользовательской реакции
                if self.status == 'user' and names_list.count(USER_EMOJI) >= USER_FORCE or self.check_for_admin(payload.member) and self.check_for_admin_mode(message) and self.status == 'user':
                    await self.send_to(self.destination, message, self.status)
                    info(f"Message with ID {message.id} was added to featured messages")
                # Проверяем условия для админской реакции
                elif self.status == 'admin' and names_list.count(ADMIN_EMOJI) >= ADMIN_FORCE and self.check_for_admin(payload.member):
                    await self.send_to(self.destination, message, self.status)
                    info(f"Message with ID {message.id} was added to admin featured messages")
                elif self.status == 'super' and names_list.count(SUPER_EMOJI) >= ADMIN_FORCE and self.check_for_admin(payload.member):
                    await self.send_to(self.destination, message, self.status)
                    info(f"Message with ID {message.id} was added to super featured messages")
                elif self.status == 'plus_one' and names_list.count(PLUS_ONE_EMOJI) >= PLUS_ONE_FORCE or self.check_for_admin(payload.member) and self.check_for_admin_mode(message) and self.status == 'plus_one':
                    await self.send_to(self.destination, message, self.status)
                    info(f"Message with ID {message.id} was added to plus one messages")

async def setup(bot):
    # Устанавливаем ког в бота
    await bot.add_cog(ReactionsCog(bot))