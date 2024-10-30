
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

from cogs.moderationcog import ModerationCog as mc
from cogs.moderationcog import Report, ALERT_CHANNEL_ID





def without_spaces(string):
    return "".join(string.split())


SUBTASKS = ["del", "mute", "unmute", "unwarn", "warn", "ban"]



class DelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.output_channel: discord.TextChannel = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.output_channel = await bot.fetch_channel(ALERT_CHANNEL_ID)
        info("DelCog cog is ready")
        
    async def do_task(report, subtask, members, reason, mute_time=None):
        match subtask:
                case "warn":
                    for member in members:
                        await mc.warn(member, reason)

                case "ban": 
                    for member in members:
                        await mc.ban(member, reason)

                case "mute": 
                    for member in members:
                        await mc.mute(member, mute_time, reason)

                case "unmute":
                    for member in members:
                        await mc.unmute(member)

                case "unwarn":
                    for member in members:
                        await mc.unwarn(member)

        
    @commands.command(name="del", attrs={''}) # This is a command, like @bot.command()
    @is_moder_or_admin()
    async def ipega(self, ctx: Ctx, *args: str):
            
        members = []
        amount = 0
        subtask = "del"
        mute_time = "10m"
        reason = "Не указано"
        
        
        for a in args:
            if a.lower() == 'all':
                members.append('all')
                
            elif not a.isdigit():
                a = a.replace('<', '').replace('>', '').replace('@', '').replace('!', '')
                a = await fetch_member(int(a))
                
            if type(a) == discord.Member:
                members.append(a)
            
                
        if 'all' in members and len(members) > 1:
            return await ctx.reply("Нельзя указывать всех участников и других участников одновременно")
                
        for i, a in enumerate(args, 1):
            if i > len(members):
                continue
            else:
                if type(a) == discord.Member:
                    return await ctx.reply("Участники должны быть указны в начале команды")
                
        for i, a in enumerate(args[len(members):]):
            match i:
                case 0:
                    if a.isdigit():
                        amount = int(a)
                    elif a in SUBTASKS:
                        subtask = a
                    elif re.search(r"^\d+[a-zA-Z]", a):
                        mute_time = a
                    else:
                        reason = a
                case 1:
                    if a in SUBTASKS:
                        subtask = a
                    elif re.search(r"^\d+[a-zA-Z]", a):
                        mute_time = a
                    else:
                        reason = a
                case 2:
                    if re.search(r"^\d+[a-zA-Z]", a):
                        mute_time = a
                    else:
                        reason = a
                case 3:
                    reason = a
                    
        await self._ipega(ctx, members, amount, subtask, mute_time, reason)
            
                
    
    async def _ipega(self, ctx: Ctx, members: typing.Optional[list[discord.Member]] = None, amount: typing.Optional[int] = 0, subtask: typing.Optional[str] = "del", mute_time: typing.Optional[str] = "10m", reason: typing.Optional[str] = "Не указано"):
        
        # Проверка на указание участников, сообщения или количество сообщений
        if not members and not ctx.message.reference and not amount:
            return await ctx.reply("Укажите участников, либо ответьте на сообщение, либо укажите кол-во сообщений")


        if subtask not in SUBTASKS:
            reason = subtask
            subtask = "del"
            
        
        after_reports = None
        output_channel = self.output_channel

        member = None
        mentioned_message = None
        is_only_reference_member = False
        members_is_all = False


        if ctx.message.reference and not amount:
            if not members:
                mentioned_message = await ctx.fetch_message(ctx.message.reference.message_id)
                member = mentioned_message.author
                is_only_reference_member = True
                await self.do_task(subtask=subtask, members=[member], reason=reason, mute_time=mute_time)
        
                report = Report(member)

            # Если команда `?del all` для удаления сообщений от всех
            elif members == ["all"]:
                report = Report(None)
                mentioned_message = await ctx.fetch_message(ctx.message.reference.message_id)
                members_is_all = True
            else:
                report = Report(None)
                await self.do_task(subtask=subtask, members=members, reason=reason, mute_time=mute_time)
                
                mentioned_message = await ctx.fetch_message(ctx.message.reference.message_id)
                
                messages_before_mentioned = 0
                async for message in ctx.history(limit=None):
                    if message == mentioned_message:
                        break
                    messages_before_mentioned += 1
                amount = messages_before_mentioned



        
        # Удаление без указанных участников
        async def delete_without_members():
            ic("delete_without_members")
            members = []

            async def foo():
                await ctx.channel.purge(limit=amount + 1, check=lambda msg: msg != ctx.message)

            for message in messages:
                if message == ctx.message:
                    messages.remove(message)
                if message.author not in members:
                    members.append(message.author)
                if f"<@{message.author.id}>" not in members_references:
                    members_references.append(f"<@{message.author.id}>")
            
            await main_report.upload_all(messages)
                    
            await self.do_task(subtask=subtask, members=members, reason=reason, mute_time=mute_time)
        

            return await foo()

        async def create_imgs_without_members():
            imgs = []
            for message in messages:
                if message == ctx.message:
                    continue
                img = await report.create_img((message,))
                if img:
                    imgs.append(img)
            return imgs
        # Основной отчет
            
        
        main_report_message = None
        main_report_title = None


        await ctx.message.add_reaction("🔄")
        async with ctx.typing():
            messages = [i async for i in ctx.history(limit=amount + 1)]

        report = Report(None)
        main_report = Report(None)
        imgs = []
        members_references = []
        all_messages_to_delete = []
        
        if members:
            if members_is_all:
                mentioned_message = await ctx.fetch_message(ctx.message.reference.message_id)
                authors = []
                async with ctx.typing():
                    async_messages = [message async for message in ctx.history(limit=1500)]
                    async_messages.sort(key=lambda m: m.created_at)
                    #async_messages.reverse()
                    
                    for i, message in enumerate(async_messages):
                        if message == mentioned_message:
                            async_messages = async_messages[:i+1]
                            amount = len(async_messages)
                            break
                    else:
                        return await ctx.reply("Не удалось найти сообщение")
                    
                    imgs = []
                    for message in async_messages:
                        if not message.author in authors:
                            authors.append(message.author)
                            
                        img = await report.create_img((message,))
                        
                        if img:
                            imgs.append(img)
                            
                        all_messages_to_delete.append(message)
                        
                await self.do_task(subtask=subtask, members=authors, reason=reason, mute_time=mute_time)
                
                for a in authors:
                    members_references.append(f"<@{a.id}>")
                    
                async def foo():
                    await ctx.channel.delete_messages(all_messages_to_delete)
                    await ctx.message.delete()
                    
            else:
                p = 0
                for i, m in enumerate(messages[:]):
                    if m == ctx.message: 
                        messages.pop(i-p)
                        p += 1
                    elif m.author not in members:
                        messages.pop(i-p)
                        p += 1
                
                if not messages:
                    await ctx.message.add_reaction("❌")
                    return await ctx.reply("Не удалось найти сообщения в указанном диапазоне😶", delete_after=3)

                imgs = await create_imgs_without_members()
                
                for m in members:
                    members_references.append(f"<@{m.id}>")

                async def foo():
                    await ctx.channel.delete_messages(messages)
                            
            after_reports = foo
            
        else:
            imgs = await create_imgs_without_members()
            
            report = Report(None)
            after_reports = delete_without_members

        for member in members_references:
            member = await fetch_member(int(member.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
            report.title=f"[{report.time}] Репорт на {member.name}"
            report.desc=("Участник", f"<@{member.id}>")
            report.desc=("Команда", subtask)
            report.desc=("Причина", reason)

            messages_deleted = 0
            messages_to_delete = []

            async for message in ctx.history(limit=None):
                if message.author == member and message is not ctx.message:
                    messages_to_delete.append(message)
                    messages_deleted += 1
                if messages_deleted == amount:
                    break

            if messages_to_delete:
                reversed_messages = list(reversed(messages_to_delete))
                image = await report.create_img(reversed_messages)
                await report.upload_all(reversed_messages)
                report.set_image(image)

            report.desc=("Кол-во удалённых сообщений", amount)

        await after_reports()

        

        main_report.set_image(imgs)
        main_report.title=f"[{report.time}] Танцуют все"
        main_report.desc=("Участники", " ".join(members_references))
        main_report.desc=("Команда", subtask)
        main_report.desc=("Причина", reason)
        main_report.desc=("Кол-во удалённых сообщений", amount)

        main_report_message = await main_report.send(output_channel=output_channel)
        main_report_title = main_report.title



        # Отправляем отчет для каждого участника

        if not main_report_message.thread:
            thread = await main_report_message.create_thread(name=main_report_title)
        else:
            thread = main_report_message.thread
            
        await main_report.send(output_channel=thread)
        
        
        if not all_messages_to_delete:
            await ctx.message.delete()



    

        
async def setup(bot):
    await bot.add_cog(DelCog(bot))
