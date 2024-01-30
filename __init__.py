import discord
import colorama 
import asyncio
import importlib.util
import os
import sys

#from TOKEN import TOKEN # Раскомментируйте эту строку если вы используете TOKEN.py внутри рабочей директории
from bot_params import PREFIX
from _con_message_base import *
from _functions_base import *

from discord.ext import commands
from colorama import Fore, Style, Back
from icecream import ic


AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + '\TOKEN.py'

colorama.init(autoreset=True)
intents = discord.Intents.default()

bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=discord.Intents.all())

spec = importlib.util.spec_from_file_location('AUTH', AUTH_FILE_PATH)
auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth)
TOKEN = auth.TOKEN

ic(discord.__version__)