from __init__ import *

import itertools
import textwrap
import datetime
import urllib
import random
import typing
import time 

from PIL import Image, ImageDraw, ImageOps, ImageFont
from dataclasses import dataclass
from discord import app_commands
from discord.ext import tasks
from io import BytesIO


ALERT_CHANNEL_ID = 1293280164314353734#1293565083850641514

WARN_LIMIT = 3
WARN_TIMEOUT_TIME = 30 # Дни тайм-аута за WARN_LIMIT предупреждений.
WARN_TIMEOUT_STEP = 1 # Время тайм-аута за предупреждения будет разбито на тайм-ауты по столько дней

def without_spaces(string):
    return "".join(string.split())



class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.alert_channel: discord.TextChannel = None

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        self.alert_channel = self.bot.get_channel(ALERT_CHANNEL_ID)
        info("Moderation cog is ready")
        
    @tasks.loop(hours=WARN_TIMEOUT_STEP)
    async def check_warns(self):
        connection = sqlite3.connect("cogs/delcog/warns.db")
        cursor = connection.cursor()

        connection.execute(""" CREATE TABLE IF NOT EXISTS users (member_id INTEGER, warns INTEGER, guild_id INTEGER); """)       # имя : кол-во предупреждений : guild_id
        connection.execute(""" CREATE TABLE IF NOT EXISTS banned (member_id INTEGER, banned_for INTEGER, guild_id INTEGER); """) # имя : отбыто дней в бане    : guild_id

        cursor.execute("SELECT member_id, banned_for, guild_id FROM banned")
        banned_list = cursor.fetchall()

        for record in banned_list:
            member_id = record[0]
            banned_for = record[1]
            guild_id = record[2]

            member = await fetch_member(member_id)

            
            if banned_for == WARN_TIMEOUT_TIME:
                await member.timeout(None)
                cursor.execute(f"DELETE FROM banned WHERE member_id={member_id}")
            else:
                cursor.execute(f"DELETE FROM banned WHERE member_id={member_id}")
                cursor.execute(f"INSERT INTO banned (member_id, banned_for) VALUES (?, ?)", (member_id, banned_for + WARN_TIMEOUT_STEP,))
                await member.timeout(datetime.timedelta(hours=WARN_TIMEOUT_STEP), reason=f"До разблокировки осталось {WARN_TIMEOUT_TIME - banned_for} дней.")

        connection.commit()
        connection.close()
        
    @commands.command()
    @is_moder_or_admin()
    async def mute(self, ctx, member: discord.Member, mute_time: str, reason: str):
        report = Report(None)
        postfix = mute_time[-1] # обозначение единицы времени
        scalar = int(mute_time[:-1]) # кол-во единиц времени

        match postfix:
            case "s":
                time_delta = datetime.timedelta(seconds=scalar)
            case "m":
                time_delta = datetime.timedelta(minutes=scalar)
            case "h":
                time_delta = datetime.timedelta(hours=scalar)
            case "d":
                time_delta = datetime.timedelta(days=scalar)

        report.desc("Время тайм-аута", mute_time) # изменение сведений репорта
        await member.timeout(time_delta, reason=reason)
        await ctx.send(f"Чувак <@{member.id}> в муте на {mute_time}. Причина: {reason}")
    
    @commands.command()
    @is_moder_or_admin()
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"Чувак <@{member.id}> снова с нами.")   
        await self.alert_channel.send(f"### UNMUTE\nЧувак <@{member.id}> снова с нами.")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx: Ctx, member: discord.Member, reason):
        await member.kick(reason=reason)
        await ctx.send(f"Чувак <@{member.id}> кикнут.")
        await self.alert_channel.send(f"## KICK\nЧувак <@{member.id}> кикнут. Причина: {reason}")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx: Ctx, member: discord.Member, reason):
        await member.ban(reason=reason)
        await ctx.send(f"Чувак <@{member.id}> забанен.")
        await self.alert_channel.send(f"## BAN\nЧувак <@{member.id}> забанен. Причина: {reason}")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx: Ctx, member: discord.Member, reason):
        await ctx.guild.unban(discord.Object(id=int(member.id)), reason=reason)
        await ctx.send(f"Чувак <@{member}> разбанен.")
        await self.alert_channel.send(f"## UNBAN\nЧувак <@{member}> разбанен. Причина: {reason}")
        
    @commands.command()
    @is_moder_or_admin()
    async def warn(self, ctx, member: discord.Member, reason):
        report = Report(None)
        connection = sqlite3.connect("cogs/delcog/warns.db")
        cursor = connection.cursor()

        cursor.execute(f"SELECT member_id, warns FROM users WHERE member_id={member.id}")
        record = cursor.fetchone()
        cursor.execute(f"DELETE FROM users WHERE member_id={member.id}")
        

        if record: # если запись существует - прибавить предупреждение к ней
            warns = record[1] + 1
        else: # иначе - создать новую запись
            warns = 1

        report.desc("Кол-во предупреждений", f"{warns}/{WARN_LIMIT}") # изменение сведений в репорте
        await ctx.send(f"Чуваку <@{member.id}> выдано предупреждение ({warns}/{WARN_LIMIT}).")
        cursor.executemany("INSERT INTO users (member_id, warns, guild_id) VALUES (?, ?, ?)", ((member.id, warns, member.guild.id), ))

        if warns >= WARN_LIMIT:
            banned_for = 0

            cursor.execute(f"DELETE FROM users WHERE member_id={member.id}") # снять с учёта кол-ва предупреждений
            cursor.execute("INSERT INTO banned (member_id, banned_for, guild_id) VALUES (?, ?, ?)", (member.id, banned_for, member.guild.id)) # начать учёт отбытого срока

            report.desc("Забанен на", f"{WARN_TIMEOUT_TIME} дней")
            await member.timeout(datetime.timedelta(hours=WARN_TIMEOUT_STEP), reason="Превышен лимит предупреждений") 
            await ctx.send(f"Превышен лимит предупреждений. Чувак <@{member.id}> в муте на {WARN_TIMEOUT_TIME} дней.")

        connection.commit()
        connection.close()
        
    @commands.command()
    @is_moder_or_admin()
    async def unwarn(self, ctx, member: discord.Member):
        connection = sqlite3.connect("cogs/delcog/warns.db")
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM banned WHERE member_id={member.id}")
        cursor.execute(f"DELETE FROM users WHERE member_id={member.id}")
        connection.commit()
        connection.close()
        await ctx.send(f"Чувак <@{member.id}> помилован. Все предупреждения сброшены.")
        await self.alert_channel.send(f"### UNWARN\nЧувак <@{member.id}> помилован. Все предупреждения сброшены.")
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))