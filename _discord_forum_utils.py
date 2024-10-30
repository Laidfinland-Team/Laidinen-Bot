import datetime

from functools import wraps

import discord
import discord.ext
import asyncio


from discord.ext import commands
from accessify import protected, private
from dataclasses import dataclass
from bot_params import (
    DEBUG_MODE, 
    MAIN_COLOR, 
    HELLCAT_ID, 
    FORUM_CATEGORY_ID,
    MODERATOR_ROLE_ID, 
    GUILD_ID, 
    jerusalem_tz
)
from modules.logger import Logger
from _functions_base import *



def is_forum_thread(func):
    def wrapper(*args, **kwargs):
        if type(kwargs['channel']) == discord.Thread and kwargs['channel'].category_id == FORUM_CATEGORY_ID: 
            result = func(*args, **kwargs)
            return result
        else:
            raise AttributeError("This function can be used only in forum threads")
    return wrapper

"""Классы для инструментов форума"""

class ForumMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value):  # Проверяем, что это метод (функция)
                dct[key] = is_forum_thread(value)  # Оборачиваем в декоратор
        return super().__new__(cls, name, bases, dct)

class ForumUtils(metaclass=ForumMeta):  
    
    @staticmethod
    async def get_author(channel: discord.Thread):
        message = await ForumUtils.find_first_message(channel)
        return message.author
    
    @staticmethod
    async def author_is_hellcat(channel: discord.Thread):
        message = await ForumUtils.find_first_message(channel)
        author = message.author
        return author.id == HELLCAT_ID

    @staticmethod
    async def author_is_admin(channel: discord.Thread):
        message = await ForumUtils.find_first_message(channel)
        author = message.author
        return author.guild_permissions.administrator
    
    @staticmethod
    async def author_is_moderator(channel: discord.Thread):
        message = await ForumUtils.find_first_message(channel)
        author = message.author
        return MODERATOR_ROLE_ID in [r.id for r in author.roles]
    
    @staticmethod
    async def find_first_message(channel: discord.Thread):
        async for message in channel.history(limit=1, oldest_first=True):
            return message
        
    @staticmethod
    async def find_last_message(channel: discord.Thread):
        async for message in channel.history(limit=1):
            return message
        
    @staticmethod
    async def fetch_messages(channel: discord.Thread):
        messages = [message async for message in channel.history(limit=None)]
        return messages    
        
    @staticmethod
    async def fetch_count_of_messages(channel: discord.Thread):
        count = 0
        async for message in channel.history(limit=None):
            count += 1
        return count
    
    
class ForumThread(discord.Thread, ForumUtils, metaclass=ForumMeta):
    async def __init__(self, channel: discord.Thread):
        
        super().__init__(guild=channel.guild, state=channel._state, data=channel.to_data())
        discord.Thread()
        
        
        self.channel = channel
        self.author = await self.get_author(self.channel)
        self.is_hellcat = False
        self.is_admin = False
        self.is_moderator = False
        self.first_message = None
        self.last_message = None
        self.count_of_messages = await self.fetch_count_of_messages(self.channel)
        
    async def get_info(self):
        self.author = await self.get_author(self.channel)
        self.is_hellcat = await self.author_is_hellcat(self.channel)
        self.is_admin = await self.author_is_admin(self.channel)
        self.is_moderator = await self.author_is_moderator(self.channel)
        self.first_message = await self.find_first_message(self.channel)
        self.last_message = await self.find_last_message(self.channel)
        self.count = await self.count_of_messages(self.channel)
        
    async def delete(self, reason: str):
        await self.channel.delete(reason=reason)
        
    async def lock(self, reason: str):
        await self.channel.edit(archived=True, reason=reason)
        
    async def unlock(self, reason: str):
        await self.channel.edit(archived=False, reason=reason)
        
    async def send_report(self, reason: str, output_channel: discord.TextChannel):
        report = Report(self.author, output_channel)
        await report.create_img(await self.channel.history(limit=None).flatten())
        await report.upload_all(await self.channel.history(limit=None).flatten())
        report.title = f"Тред удален командой"
        report.desc = ("Удалил", self.author.mention)
        report.desc = ("Причина", reason)
        return await report.send(output_channel)
        
    async def send_report_and_delete(self, reason: str, output_channel: discord.TextChannel):
        report = await self.send_report(reason, output_channel)
        await self.delete(reason)
        return report

    async def send_report_and_lock(self, reason: str, output_channel: discord.TextChannel):
        report = await self.send_report(reason, output_channel)
        await self.lock(reason)
        return report

    async def send_report_and_unlock(self, reason: str, output_channel: discord.TextChannel):
        report = await self.send_report(reason, output_channel)
        await self.unlock(reason)
        return report

    async def send_report_and_lock_and_delete(self, reason: str, output_channel: discord.TextChannel):
        report = await self.send_report(reason, output_channel)
        await self.lock(reason)
        await self.delete(reason)
        return report