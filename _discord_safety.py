import discord
import discord.ext
import discord.ext.commands

from pretty_help import PrettyHelp

from bot_params import PREFIX, HELLCAT_ID, MAIN_COLOR
from _discord_functions_base import Ctx
from logging import Logger


enabled_bot = discord.ext.commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all(), help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"))
disabled_bot = discord.ext.commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all(), help_command=None)

log = Logger("log.log")

"""Проверка упоминаний"""
async def mentions_check(ctx: Ctx):
    if ctx.message.mention_everyone or ctx.message.role_mentions:
        if ctx.message.author.id != HELLCAT_ID:
            await ctx.reply("Нельзя упомянуть всех 🤐")
            return False
    log.info(f"Command {ctx.command} was executed by {ctx.author} in {ctx.channel}")
    return True