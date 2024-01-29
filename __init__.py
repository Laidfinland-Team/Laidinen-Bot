import discord
import colorama 
import asyncio
import os

from TOKEN import TOKEN
from bot_params import PREFIX
from _con_message_base import *
from _functions_base import *

from discord.ext import commands
from colorama import Fore, Style, Back
from icecream import ic

colorama.init(autoreset=True)
intents = discord.Intents.default()

bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=discord.Intents.all())

ic(discord.__version__)