import discord
from discord.ext import commands

import random
import json

from __init__ import *

DB_DIR = r"light_databases\featured_messages.json"
CONFIG_DIR = r"reactionscog\reactions.json"

# ID канала для отправки сообщений в чат
CHAT_CHANNEL_ID = 1156973544891220088
# ID канала для отправки сообщений в форум
FORUM_CHANNEL_ID = 1156973544891220088

# Порог количества реакций для админов и пользователей
ADMIN_FORCE = 1
USER_FORCE = 7

# Категории
FORUMS = 1180846730602889236
NOTCHATS = [1156902879530070107, 1221874671352545320, 1156945170969931847, 1273188151786995712]

# Цвета для эмбедов
ADMIN_COLOR = discord.Color.red()
USER_COLOR = discord.Color.yellow()

class ReactionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.destination = None  # Место назначения (чат или форум)
        self.status = None  # Статус реакции (админская или пользовательская)

        # Загружаем конфигурацию кога
        with open(CONFIG_DIR, "r") as f:
            self.config = json.load(f)

        # Эмодзи для реакций
        self.ADMIN_EMOJI = self.config["emoji"]["favorite"]["admin"]
        self.USER_EMOJI = self.config["emoji"]["favorite"]["user"]
    def check_for_featured(self, message: discord.Message):
        # Проверяем, было ли сообщение уже добавлено в избранное
        with open(DB_DIR, "r") as f:
            featured_messages = json.load(f)
        return message.id in featured_messages
    
    def check_for_admin(self, member: discord.Member):
        # Проверяем, является ли пользователь администратором
        return member.guild_permissions.administrator
    
    def add_to_featured(self, message: discord.Message):
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

    async def send_to(self, destination: str, message: discord.Message, status: str):
        # Отправляем сообщение в заданное место назначения
        title = self.config["messages"]["title"]["favorite"]
        description = self.config["messages"]["description"]["favorite"]
        content = f"{'<:AA_featured:1284934932413550612>' if status == 'user' else '<:AA_admin_featured:1284934964445577308>'}"

        embed = discord.Embed(
            title=title[f"{destination}"].format("" if status == 'user' else title["admin"]),
            description=description.format(message.content, message.jump_url),
            color=USER_COLOR if status == 'user' else ADMIN_COLOR
        ).set_author(name=message.author.display_name)
        
        if destination == 'forum':
            # Отправляем в форум
            channel = self.bot.get_channel(FORUM_CHANNEL_ID)
            await channel.send(embed=embed, content=content)
        elif destination == 'chat':
            # Отправляем в чат
            channel = self.bot.get_channel(CHAT_CHANNEL_ID)
            await channel.send(embed=embed, content=content)
        
        # Если сообщение еще не в избранном, добавляем его
        if not self.check_for_featured(message):
            self.add_to_featured(message)
    
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
        if ic(ic(payload.emoji.name) == ic(self.USER_EMOJI)):
            self.status = 'user'
        elif payload.emoji.name == self.ADMIN_EMOJI:
            self.status = 'admin'
        
        # Определяем место назначения
        if channel.category_id == FORUMS:
            self.destination = 'forum'
        elif channel.category_id not in NOTCHATS:
            self.destination = 'chat'
        
        ic(message.reactions)
        ic(len(message.reactions))
        
        # Если сообщение еще не в избранном
        if not self.check_for_featured(message):
            if ic(self.destination):
                names_list = []
                # Собираем имена всех эмодзи в реакциях
                for reaction in message.reactions:
                    names_list.append(reaction.emoji.name) if type(reaction.emoji) is not str else None
                # Проверяем условия для пользовательской реакции
                if self.status == 'user' and names_list.count(self.USER_EMOJI) >= USER_FORCE:
                    await self.send_to(self.destination, message, self.status)
                # Проверяем условия для админской реакции
                elif self.status == 'admin' and names_list.count(self.ADMIN_EMOJI) >= ADMIN_FORCE and self.check_for_admin(payload.member):
                    await self.send_to(self.destination, message, self.status)

async def setup(bot):
    # Устанавливаем ког в бота
    await bot.add_cog(ReactionsCog(bot))