import discord
import discord.ext
import discord.ext.commands

from pretty_help import PrettyHelp

from bot_params import PREFIX, HELLCAT_ID, MAIN_COLOR
from _discord_functions_base import Ctx


enabled_bot = discord.ext.commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all(), help_command=None)
disabled_bot = discord.ext.commands.Bot(command_prefix=PREFIX, intents=discord.Intents.default(), help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"))


"""Проверка упоминаний"""
async def mentions_check(ctx: Ctx):
    if ctx.message.mention_everyone or ctx.message.role_mentions:
        if ctx.message.author.id != HELLCAT_ID:
            await ctx.reply("Нельзя упомянуть всех 🤐")
            return False
    return True